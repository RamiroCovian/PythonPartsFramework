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

"""Exposed classes and functions from NemAll_Python_Geometry"""

from __future__ import annotations

import typing

import enum
import collections.abc

import NemAll_Python_Utility

from TestHelper import PythonPartPylintDecorator
from TypeCollections import PolyhedronTypesList
from TypeCollections import Curve3DList


__all__ = [
    "ASET_BREP_TESSELATION",
    "ASET_MAX_DISTANCE",
    "ASET_MAX_LENGTH",
    "ASET_SEGMENTATION",
    "AddToMinMax",
    "Angle",
    "AngleList",
    "ApproximationSettings",
    "Arc2D",
    "Arc2DList",
    "Arc3D",
    "Arc3DList",
    "Axis2D",
    "Axis3D",
    "AxisPlacement2D",
    "AxisPlacement2DList",
    "AxisPlacement3D",
    "AxisPlacement3DList",
    "BOTTOM_2D",
    "BRep3D",
    "BRep3DBuilder",
    "BRep3DList",
    "BSpline2D",
    "BSpline2DList",
    "BSpline3D",
    "BSpline3DList",
    "BSpline3DService",
    "BSplineSurface3D",
    "BSplineSurface3DList",
    "BoundingBox2D",
    "BoundingBox2DList",
    "CalcAngle",
    "CalcArea",
    "CalcLength",
    "CalcMass",
    "CalcMinMax",
    "CalcProjectedMinMax",
    "CalcSurface",
    "CalcVolume",
    "CalculateNormal",
    "CalculateSplineLengthToPoint",
    "CenterCalculus",
    "ChamferCalculus",
    "ClippedSweptSolid3D",
    "ClippedSweptSolid3DList",
    "Clipping",
    "ClosedArea2D",
    "ClosedArea2DList",
    "ClosedArea3D",
    "ClosedArea3DList",
    "ClosedAreaComposite2D",
    "ClosedAreaComposite2DList",
    "ClosedAreaComposite3D",
    "ClosedAreaComposite3DList",
    "Clothoid2D",
    "Clothoid2DList",
    "Colliding",
    "Comparison",
    "Cone3D",
    "Cone3DList",
    "ConicalSurface3D",
    "ConicalSurface3DList",
    "Convert3DRotation",
    "ConvertTo2D",
    "ConvertTo3D",
    "ConvertToBSpline2D",
    "CreateBRep3D",
    "CreateFrustumOfPyramid",
    "CreateLoftedBRep3D",
    "CreatePatchBRep3D",
    "CreatePlanarBRep3D",
    "CreatePlanarSurface",
    "CreatePolygon3D",
    "CreatePolygon3DFromIndex",
    "CreatePolyhedron",
    "CreatePolyline3D",
    "CreatePolyline3DFromIndex",
    "CreateRailSweptBRep3D",
    "CreateRevolvedBRep3D",
    "CreateSweptBRep3D",
    "CreateSweptPolyhedron3D",
    "Cuboid3D",
    "Cuboid3DList",
    "CutBrepWithPlane",
    "CutPolyhedronWithPlane",
    "Cylinder3D",
    "Cylinder3DList",
    "DEFAULT_NORM_TYPE",
    "DeletePolyhedronLastFace",
    "DivisionPoints",
    "END_POINT",
    "Ellipsoid3D",
    "Ellipsoid3DList",
    "ExtrudedAreaSolid3D",
    "ExtrudedAreaSolid3DList",
    "FAILED_TO_CONVERGE",
    "FAILED_TO_INVERT_MATRIX",
    "FREE_3D",
    "FRONT_2D",
    "FT_CC_CONCETRIC",
    "FT_CC_NO_INTERSECTION",
    "FT_CC_ONE_INTERSECTION",
    "FT_CC_TWO_INTERSECTION",
    "FT_KK_KURVE_ELEMENTS",
    "FT_KK_PARALLEL_KURVE_ELEMENTS",
    "FT_LC_NO_INTERSECTION",
    "FT_LC_ONE_INTERSECTION",
    "FT_LC_TWO_INTERSECTION",
    "FT_LL_INTERSECTION_AT_THE_END",
    "FT_LL_INTERSECTION_ON_LINE",
    "FT_LL_INTERSECTION_OUT_OF_LINES",
    "FT_LL_PARALLEL_LINES",
    "FT_UNKNOWN",
    "FaceOffset",
    "FaceShell",
    "FilletCalculus2D",
    "FilletCalculus3D",
    "FindMinDistancePoint",
    "GeometryEdge",
    "GeometryEdgeList",
    "GetAbsoluteTolerance",
    "GetAllIntersections",
    "GetAngleTolerance",
    "GetClosestIntersection",
    "GetCurvatureTolerance",
    "GetCurveLengthTolerance",
    "GetIntersectionPoints",
    "GetRelativeTolerance",
    "GetRotationMatrix",
    "GroundViewHiddenCalculation",
    "HATCHING_MEASUR_NORM_TYPE",
    "HATCHING_NORM_TYPE",
    "HSET_NOMODIFY",
    "HSET_TILT",
    "HSET_TRIANGULATE",
    "HSET_UNKNOWN",
    "HealingSettings",
    "HiddenCalculationParameters",
    "HiddenCalculus",
    "HiddenMaterial",
    "INVALID_CONE",
    "INVALID_CUBOID",
    "INVALID_CYLINDER",
    "INVALID_ELLIPSOID",
    "INVALID_GEOOBJECT",
    "INVALID_LINE",
    "INVALID_POINT",
    "INVALID_POINTCLOUD",
    "INVALID_POLYGON",
    "INVALID_POLYHEDRON",
    "INVALID_POLYLINE",
    "INVALID_SURFACE",
    "IS_ABOVE",
    "IS_BELOW",
    "IS_IN",
    "IS_UNKNOWN",
    "ImprintProfileOnFaces",
    "Intersect",
    "IntersectRayBRep",
    "IntersectRayPolyhedron",
    "IntersectRayPolyhedronFlag",
    "Intersecting",
    "IntersectingRel",
    "IntersectionCalculus",
    "IntersectionCalculusEx",
    "IntersectionRayBRep",
    "IntersectionRayPolyhedron",
    "IsCoplanar",
    "Kanten_t",
    "LEFT_2D",
    "Line2D",
    "Line2DList",
    "Line3D",
    "Line3DList",
    "LineHelpConstruction",
    "MakeBoolean",
    "MakeIntersection",
    "MakeSectionWithSurfaces",
    "MakeSubtraction",
    "MakeUnion",
    "Matrix2D",
    "Matrix3D",
    "Matrix3DList",
    "MinMax2D",
    "MinMax2DList",
    "MinMax3D",
    "Mirror",
    "Move",
    "MoveArc3DToZ0Plane",
    "MoveSpline3DToZ0Plane",
    "NEGATIVE_ORIENTATION",
    "NO_ERR",
    "Offset",
    "Offset3DPlane",
    "OffsetCurve",
    "OrientedEdge",
    "OrientedEdgeList",
    "PARALLEL_LINES",
    "PHSET_NOMODIFY",
    "PHSET_NORMALIZE",
    "POSITIVE_ORIENTATION",
    "Path",
    "Path2D",
    "Path2DList",
    "Path3D",
    "Path3DList",
    "PathIterator",
    "PerpendicularCalculus",
    "Plane3D",
    "Point2D",
    "Point2DList",
    "Point3D",
    "Point3DList",
    "PolyPoints2D",
    "PolyPoints3D",
    "Polygon2D",
    "Polygon2DList",
    "Polygon2DUtil",
    "Polygon3D",
    "Polygon3DList",
    "PolygonalArea",
    "PolygonalArea2D",
    "PolygonalArea2DList",
    "PolygonalArea3D",
    "PolygonalArea3DList",
    "Polygonize",
    "PolygonizeEqually",
    "Polyhedron3D",
    "Polyhedron3DBuilder",
    "Polyhedron3DList",
    "PolyhedronFace",
    "PolyhedronType",
    "PolyhedronUtil",
    "Polyline2D",
    "Polyline2DList",
    "Polyline2DUtil",
    "Polyline3D",
    "Polyline3DList",
    "REAR_2D",
    "RIGHT_2D",
    "Rotate",
    "SIDEFACE_NORM_TYPE",
    "STARTPOINT_NORM_TYPE",
    "START_POINT",
    "SetAbsoluteTolerance",
    "SetAngleTolerance",
    "SetCurvatureTolerance",
    "SetCurveLengthTolerance",
    "SetRelativeTolerance",
    "SetZValue",
    "Spline2D",
    "Spline2DList",
    "Spline3D",
    "Spline3DList",
    "Split",
    "SplitPolygon3DToParts",
    "SweepRotationType",
    "TOP_2D",
    "TangentCalculus",
    "Tesselate",
    "Touching",
    "Transform",
    "TransformCoord",
    "Trim",
    "VS_COLINEAR",
    "VS_NOT_COPLANAR",
    "Vector2D",
    "Vector2DList",
    "Vector3D",
    "Vector3DList",
    "X_COORD",
    "Y_COORD",
    "ZERO_ANGLE",
    "Z_COORD",
    "eAbove",
    "eAllocError",
    "eAntiParallel",
    "eApproximationSettingsType",
    "eBelow",
    "eBoolOpResult",
    "eBoxPoint",
    "eCenter",
    "eClip",
    "eClothoid",
    "eClothoidType",
    "eComparisionResult",
    "eCoordIdentification",
    "eCreatePatchResult",
    "eCrossing",
    "eERROR_LINES_ARENOT_COPLANAR",
    "eERROR_LINES_ARE_COLLINEAR",
    "eERROR_LINES_ARE_NOT_PARALLEL",
    "eERROR_LINES_ARE_PARALLEL",
    "eERROR_NO_FILLET_CREATED",
    "eERROR_ZEROO_LINE_LENGTH",
    "eEqualToEndPoint",
    "eEqualToStartPoint",
    "eError",
    "eFilletErrorCode",
    "eFilletType",
    "eGeometryErrorCode",
    "eHidden",
    "eHiddenCalculationResult",
    "eInside",
    "eInvalid3DLine",
    "eLeft",
    "eLeftBottom",
    "eLeftTop",
    "eLinePointIdentification",
    "eMiddleBottom",
    "eMiddleLeft",
    "eMiddleRight",
    "eMiddleTop",
    "eNO_ERROR",
    "eNegativeIfNoPositive",
    "eNegativePreferred",
    "eNegativeVerticalPreferred",
    "eNoPlane",
    "eNotParallel",
    "eOK",
    "eOnElement",
    "eOutOfRange",
    "eOutside",
    "eParabolaGeneral",
    "eParabolaQuadratic",
    "eParallel",
    "ePlanarSurfaceError",
    "ePolygonHealingSettings",
    "ePolygonNormalizeType",
    "ePolyhedronHealingSettings",
    "ePositiveOnly",
    "eProjectionMatrixType",
    "eRight",
    "eRightBottom",
    "eRightTop",
    "eServiceResult",
    "eSmallestLmabda",
    "eSplitInvalidArgs",
    "eSplitInvalidGeometry",
    "eSplitNone",
    "eSplitOk",
    "eSplitResult",
    "eStructuralError",
    "eSurfaceTrimParam",
    "eTrimUMaxValue",
    "eTrimUMaxValueReverse",
    "eTrimUMinValue",
    "eTrimUMinValueReverse",
    "eTrimUndefined",
    "eTrimVMaxValue",
    "eTrimVMaxValueReverse",
    "eTrimVMinValue",
    "eTrimVMinValueReverse",
    "eUnknown",
    "eValidationStatusPolygon3D",
    "eVisible",
    "eWarpedPolygonalFace",
    "eWrongShape",
    "eXY",
    "eXZ",
    "eYZ",
    "tEdges",
    "tFaces",
    "tInvalid",
    "tVolume"
]


class Angle():
    """Representation class for angle in [rad].
    """
    @staticmethod
    def DegToRad(angleDeg: float) -> float:
        """Convert angle from deg to rad

        Can be used for initialization of Angle class with deg angle.

        angle = Angle(Angle.DegToRad(45));  // angle will be 0.75[rad] (approx.)

        Args:
            angleDeg: Angle in deg

        Returns:
            Angle in rad
        """
    @staticmethod
    def FromDeg(angleDeg: float) -> Angle:
        """Args:
            angleDeg: Angle in degree

        Returns:
            Angle
        """
    def Get(self) -> float:
        """Get angle as radian value.

        Returns:
            double as radian value.
        """
    def GetDeg(self) -> float:
        """Get angle as degree value.

        Returns:
            double as degree value.
        """
    def Normalize2Pi(self):
        """Normalize the angle to a range of <0, 2PI>.

        This method is checked and set Angle to 0
        while angle is out of range <-1e8, 1e8>. The algorithm isn't stable for angle out of this range.
        """
    def NormalizePi(self):
        """Normalize the angle to a range of <-PI, PI>.

        This method is checked and set Angle to 0
        while angle is out of range <-1e8, 1e8>. The algorithm isn't stable for angle out of this range.
        """
    @staticmethod
    def RadToDeg(angleRad: float) -> float:
        """Convert angle from rad to deg

        Args:
            angleRad: Angle in rad

        Returns:
            Angle in rad
        """
    @staticmethod
    def RadToGrad(angleRad: float) -> float:
        """Convert angle from rad to grad

        Args:
            angleRad: Angle in rad

        Returns:
            Angle in grad
        """
    @typing.overload
    def Set(self, angle: float):
        """Set angle as radian value.

        Args:
            angle: angle which will be set.
        """
    @typing.overload
    def Set(self, angle: Angle):
        """Set angle as radian value.

        Args:
            angle: angle which will be set.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetDeg(self, angleDeg: float):
        """Set angle as degree value.

        Args:
            angleDeg: angle as degree value which will be set.
        """
    @typing.overload
    def __add__(self, angle: Angle) -> Angle:
        """Addition operator

        Args:
            angle: Angle which will be added

        Returns:
            New angle
        """
    @typing.overload
    def __add__(self, angle: float) -> Angle:
        """Addition operator

        Args:
            angle: Angle as double value which will be added

        Returns:
            New angle
        """
    def __add__(self, dummy: typing.Any):
        """ Overloaded function. See individual overloads.

        Args:
            dummy:  dummy parameter

        Returns:
            dummy
        """
    def __eq__(self, angle: Angle) -> bool:
        """Comparison of angles.

        Be careful, this method work without tolerance!

        Args:
            angle: angle to be compared.

        Returns:
            True when angles are equal, otherwise false.
        """
    def __float__(self) -> float:
        """Type conversion operator.

        Returns:
            Angle as double.
        """
    def __iadd__(self, angle: Angle) -> Angle:
        """Addition assignment operator.

        Args:
            angle: Angle which will be added.

        Returns:
            Reference to Angle.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, angle: Angle):
        """Copy constructor.

        Args:
            angle: angle which will be copied.
        """
    @typing.overload
    def __init__(self, angle: float):
        """Constructor.

        Initialize angle from single value

        Args:
            angle: Angle.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, angle: Angle) -> Angle:
        """Addition assignment operator.

        Args:
            angle: Angle which will be added.

        Returns:
            Reference to Angle.
        """
    def __ne__(self, angle: Angle) -> bool:
        """Comparison of angles.

        Be careful, this method work without tolerance!

        Args:
            angle: angle to be compared.

        Returns:
            True when angles are not equal, otherwise false.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Deg(self) -> float:
        """Get angle as degree value.
        """
    @Deg.setter
    def Deg(self, angleDeg: float) -> None:
        """Set angle as degree value.

        Args:
            angleDeg: angle as degree value which will be set.
        """
    @property
    def Rad(self) -> float:
        """Get angle as radian value.
        """
    @Rad.setter
    def Rad(self, angle: float) -> None:
        """Set angle as radian value.

        Args:
            angle: angle which will be set.
        """

class AngleList():
    """List for Angle objects
    """
    def __contains__(self, value: Angle) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Angle):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: AngleList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Angle:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> AngleList:
        """Add a list

        Args:
            eleList: Angle list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Angle):
        """Constructor with a Angle

        Args:
            ele: Angle
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Angle

        Args:
            eleList: Angle list
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
    def __setitem__(self, index: (int | slice), value: Angle):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Angle):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: AngleList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Angle list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class ApproximationSettings():
    """Class holding approximation options.
    """
    def GetDensity(self) -> float:
        """Get Density value

        Returns:
            density value
        """
    def GetMaxAngle(self) -> Angle:
        """Get Maximal Angle value

        Returns:
            maximal angle value
        """
    def GetMaxDistance(self) -> float:
        """Get MaxDistance value

        Returns:
            const Reference to MaxDistance value
        """
    def GetMaxLength(self) -> float:
        """Get MaxLength value

        Returns:
            const Reference to MaxLength value
        """
    def GetMinLength(self) -> float:
        """Get Minimal Length value

        Returns:
            minimal length value
        """
    def GetSegmentation(self) -> int:
        """Get Segmentation value

        Returns:
            const Reference to Segmentation value
        """
    def GetType(self) -> eApproximationSettingsType:
        """Get Type of the settings

        Returns:
            const Reference to Settings type
        """
    def IsBRepTesselation(self) -> bool:
        """Check whether the type of the settings is ASET_BREP_TESSELATION

        Returns:
            true/false.
        """
    def IsMaxDistance(self) -> bool:
        """Check whether the type of the settings is ASET_MAX_DISTANCE

        Returns:
            true/false.
        """
    def IsMaxLength(self) -> bool:
        """Check whether the type of the settings is ASET_MAX_LENGTH

        Returns:
            true/false.
        """
    def IsSegmentation(self) -> bool:
        """Check whether the type of the settings is ASET_SEGMENTATION

        Returns:
            true/false.
        """
    def SetBRepTesselation(self, density: float, maxAngle: Angle, minLength: float, maxLength: float):
        """Set all settings for BRep3D tesselation.

        Args:
            density:   new density value.
            maxAngle:  new maximal edge length value.
            minLength: new minimal edge length value.
            maxLength: new maximal angle value.
        """
    def SetMaxDistance(self, maxDistance: float):
        """Set MaxDistance value.

        Args:
            maxDistance: new MaxDistance value.
        """
    def SetMaxLength(self, maxLength: float):
        """Set MaxLength value.

        Args:
            maxLength: new MaxLength value.
        """
    def SetSegmentation(self, segmentation: int):
        """Set Segmentation.

        Args:
            segmentation: new Segmentation value.
        """
    def __eq__(self, right: ApproximationSettings) -> bool:
        """Operator ==

        Args:
            right: settings to compare

        Returns:
            true if settings are equal
        """
    @typing.overload
    def __init__(self, oType: eApproximationSettingsType = eApproximationSettingsType.ASET_SEGMENTATION, value: float = 30.0):
        """Default constructor.

        Other members will be set to 0. Types can be found in GeometryEnums.h

        Args:
            oType: Type of the settings which will be set
            value: value which will be set
        """
    @typing.overload
    def __init__(self, options: ApproximationSettings):
        """Copy constructor.

        Args:
            options: ApproximationSettings which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, right: ApproximationSettings) -> bool:
        """Operator !=

        Args:
            right: settings to compare

        Returns:
            true if settings are NOT equal
        """

class Arc2D():
    """Representation class for 2D arc.

    Arc2D could be a circular or elliptical arc. All angles are given as central angles.
    In case of an elliptical arc the ellipse angle and the central angle do not correspond.
    All start angle is normalized to the range [-PI..2PI]. The winding direction of the arc could either
    be in clockwise or in counterclockwise direction.

    Examples:

    Circular arc without axis rotation

    Circular arc with axis rotation (the same arc could be created without axis rotation
    only by increasing the start and end angles by the axis angle)

    Elliptical arc
    """
    def Close(self):
        """Close arc

        End angle will be adjusted to close arc.
        """
    def EqualRef(self, arc: Arc2D) -> bool:
        """Test for equal reference points

        Args:
            arc: Arc which will be compared

        Returns:
            result as bool
        """
    def GetAxisAngle(self) -> Angle:
        """Get the axis angle

        Returns the the angle of the major axis

        Returns:
            axis angle.
        """
    def GetCenter(self) -> Point2D:
        """Get center point

        Returns:
            center point
        """
    def GetCenterRel(self) -> Point2D:
        """Get center point in relative coordinate system.

        Returns:
            center point
        """
    def GetDeltaAngle(self) -> Angle:
        """Get difference between EndAngle and StartAngle

        Returns:
            delta angle
        """
    def GetEndAngle(self) -> Angle:
        """Get end angle

        Returns:
            end angle
        """
    def GetEndPoint(self) -> Point2D:
        """Get the end point in world coordinate system.

        Returns:
            point.
        """
    def GetEndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system

        Returns:
            constant point.
        """
    def GetEndTangent(self) -> Vector2D:
        """Get tangent vector at the end point of Arc

        Returns:
            Tangent vector (unit vector)
        """
    def GetMajorRadius(self) -> float:
        """Get major radius

        Returns:
            major radius
        """
    def GetMinorRadius(self) -> float:
        """Get minor radius

        Returns:
            minor radius
        """
    def GetPoint(self, angle: Angle) -> Point2D:
        """Get point on Arc in world coordinate system

        Calculates the point at central angle in parameter angle on the Arc

        Args:
            angle: central angle of the point

        Returns:
            point on Arc
        """
    def GetPointLocalAngle(self, pnt: Point2D) -> Angle:
        """Get local angle on arc for point in world coordinate system

        Calculates the angle of the point projected on the arc count from 0 (axis)
        with respect to the clockwise/counterclockwise orientation

        Args:
            pnt: point in space

        Returns:
            angle local angle of the point
        """
    def GetRefPoint(self) -> Point2D:
        """Get reference point

        Returns:
            reference point
        """
    def GetStartAngle(self) -> Angle:
        """Get start angle

        Returns:
            start angle
        """
    def GetStartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.

        Returns:
            point.
        """
    def GetStartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system

        Returns:
            constant point.
        """
    def GetStartTangent(self) -> Vector2D:
        """Get tangent vector at the start point of Arc

        Returns:
            Tangent vector (unit vector)
        """
    def IsAngleOnArc(self, angle: Angle) -> bool:
        """Checks if the given angle lies on the arc

        Args:
            angle: angle to test

        Returns:
            Angle on arc true/false
        """
    def IsCircle(self) -> bool:
        """Test if ellipse is circle

        Tests if major radius equals minor radius

        Returns:
            if ellipse is circle
        """
    def IsClosed(self) -> bool:
        """Check if arc is closed ( Full circle/ellipse )

        Returns:
            closed curve true/false
        """
    def IsCounterClockwise(self) -> bool:
        """Returns winding direction counterclockwise true/false

        Returns:
            Is counterclockwise true/false
        """
    def Reverse(self):
        """Reverse of current arc

        Method reverse Arc, start with end angle and orientation.
        """
    def SetAxisAngle(self, angle: Angle):
        """Set the axis angle

        Set the angle of the major axis

        Args:
            angle: axis angle
        """
    def SetCenter(self, center: Point2D):
        """Set center point

        Args:
            center: center point
        """
    def SetCenterRel(self, center: Point2D):
        """Set center point in local coordinate system

        Args:
            center: center point
        """
    def SetCounterClockwise(self, ccw: bool):
        """Set the winding direction of the arc

        Args:
            ccw: winding counterclockwise true/false
        """
    def SetEndAngle(self, angle: Angle):
        """Set end angle

        Set the end angle

        Args:
            angle: end angle
        """
    def SetEndPoint(self, endpoint: Point2D):
        """Set the end point in world coordinate system

        Args:
            endpoint: constant 2D point
        """
    def SetMajorRadius(self, radius: float):
        """Set major radius

        Args:
            radius: major radius
        """
    def SetMinorRadius(self, radius: float):
        """Set minor radius

        Args:
            radius: minor radius
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set reference point

        Args:
            refPoint: reference point
        """
    def SetStartAngle(self, angle: Angle):
        """Set start angle

        Set the start angle

        Args:
            angle: start angle
        """
    def SetStartPoint(self, startpoint: Point2D):
        """Set the start point in world coordinate system

        Args:
            startpoint: constant 2D point
        """
    def Supplement(self):
        """Convert to supplementary arc

        Orientation of arc will not be changed.
        """
    def __eq__(self, arc: Arc2D) -> bool:
        """Comparison of arcs.

        Be careful, this method work without tolerance!

        Args:
            arc: arc to be compared.

        Returns:
            True when arcs are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, arc: Arc2D):
        """Copy constructor.

        Args:
            arc: Arc2D to be copied
        """
    @typing.overload
    def __init__(self, center: Point2D, minor: float, major: float, axisangle: float, startangle: float, endangle: float,
                 counterClockwise: bool = True):
        """Constructor

        Args:
            center:           Center point
            minor:            Minor radius
            major:            Major radius
            axisangle:        Axis angle
            startangle:       Start angle
            endangle:         End angle
            counterClockwise: Direction is counter clockwise: true/false
        """
    @typing.overload
    def __init__(self, center: Point2D, radius: float, counterClockwise: bool = True):
        """Constructor for creating circle

        Create circle as arc with start angle 0 [rad] and end angle 2pi [rad].
        Minor and major radii are equal.

        Args:
            center:           Center point
            radius:           Minor radius
            counterClockwise: Direction is counter clockwise: true/false
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix2D) -> Arc2D:
        """Matrix transformation.

        Args:
            matrix: transformation matrix.

        Returns:
            transformed Arc2D.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def AxisAngle(self) -> Angle:
        """Get the axis angle

        Returns the the angle of the major axis
        """
    @AxisAngle.setter
    def AxisAngle(self, angle: Angle) -> None:
        """Returns the the angle of the major axis

        Set the axis angle

        Set the angle of the major axis

        Args:
            angle: axis angle
        """
    @property
    def Center(self) -> Point2D:
        """Get center point
        """
    @Center.setter
    def Center(self, center: Point2D) -> None:
        """Set center point

        Args:
            center: center point
        """
    @property
    def CenterRel(self) -> Point2D:
        """Get center point in relative coordinate system.
        """
    @CenterRel.setter
    def CenterRel(self, center: Point2D) -> None:
        """Set center point in local coordinate system

        Args:
            center: center point
        """
    @property
    def CounterClockwise(self) -> bool:
        """Returns winding direction counterclockwise true/false
        """
    @CounterClockwise.setter
    def CounterClockwise(self, ccw: bool) -> None:
        """Returns winding direction counterclockwise true/false

        Set the winding direction of the arc

        Args:
            ccw: winding counterclockwise true/false
        """
    @property
    def DeltaAngle(self) -> Angle:
        """Get difference between EndAngle and StartAngle
        """
    @property
    def EndAngle(self) -> Angle:
        """Get end angle
        """
    @EndAngle.setter
    def EndAngle(self, angle: Angle) -> None:
        """Set end angle

        Set the end angle

        Args:
            angle: end angle
        """
    @property
    def EndPoint(self) -> Point2D:
        """Get the end point in world coordinate system.
        """
    @EndPoint.setter
    def EndPoint(self, endpoint: Point2D) -> None:
        """Set the end point in world coordinate system

        Args:
            endpoint: constant 2D point
        """
    @property
    def EndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system
        """
    @property
    def MajorRadius(self) -> float:
        """Get major radius
        """
    @MajorRadius.setter
    def MajorRadius(self, radius: float) -> None:
        """Set major radius

        Args:
            radius: major radius
        """
    @property
    def MinorRadius(self) -> float:
        """Get minor radius
        """
    @MinorRadius.setter
    def MinorRadius(self, radius: float) -> None:
        """Set minor radius

        Args:
            radius: minor radius
        """
    @property
    def RefPoint(self) -> Point2D:
        """Get reference point
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point2D) -> None:
        """Set reference point

        Args:
            refPoint: reference point
        """
    @property
    def StartAngle(self) -> Angle:
        """Get start angle
        """
    @StartAngle.setter
    def StartAngle(self, angle: Angle) -> None:
        """Set start angle

        Set the start angle

        Args:
            angle: start angle
        """
    @property
    def StartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, startpoint: Point2D) -> None:
        """Set the start point in world coordinate system

        Args:
            startpoint: constant 2D point
        """
    @property
    def StartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system
        """

class Arc2DList():
    """List for Arc2D objects
    """
    def __contains__(self, value: Arc2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Arc2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Arc2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Arc2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Arc2DList:
        """Add a list

        Args:
            eleList: Arc2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Arc2D):
        """Constructor with a Arc2D

        Args:
            ele: Arc2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Arc2D

        Args:
            eleList: Arc2D list
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
    def __setitem__(self, index: (int | slice), value: Arc2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Arc2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Arc2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Arc2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Arc3D():
    """Representation class for 3D arc.

    The Arc3D is defined like the Arc2D. The only difference is, that the normal of the
    plane the arc is lying in might be rotated around the x-axis.
    """
    def Close(self):
        """Close the arc.

        Set the delta angle to 2Pi, to close the arc
        """
    def EqualRef(self, arc: Arc3D) -> bool:
        """Test for equal reference point

        Args:
            arc: Arc3D to compare with

        Returns:
            result as bool.
        """
    def GetCenter(self) -> Point3D:
        """Get center.

        Returns:
            Point3D center point
        """
    def GetCenterRel(self) -> Point3D:
        """Get center in relative coordinate system

        Returns:
            Point3D center point
        """
    def GetDeltaAngle(self) -> Angle:
        """Get the delta angle

        Returns:
            delta angle
        """
    def GetEndAngle(self) -> Angle:
        """Get end angle.

        Returns:
            angle as const Angle.
        """
    def GetEndPoint(self) -> Point3D:
        """Get end point in world coordinates

        Returns:
            end point.
        """
    def GetEndRelPoint(self) -> Point3D:
        """Get end point in relative coordinates

        Returns:
            End Point in relative coordinates.
        """
    def GetLocalPoint(self, point: Point3D) -> Point3D:
        """Get the local coordinates of a global world point

        Args:
            point: Global point

        Returns:
            point angle
        """
    def GetMajorAxis(self) -> Vector3D:
        """Get the major axis
          The major axis is calculated according to the plane normal and the axis angle

        Returns:
            major axis as Vector3D
        """
    def GetMajorRadius(self) -> float:
        """Get major radius.

        Returns:
            major radius as const double.
        """
    def GetMinorAxis(self) -> Vector3D:
        """Get the minor axis
          The minor axis is calculated via the cross product of major axis and plane normal

        Returns:
            minor axis as Vector3D
        """
    def GetMinorRadius(self) -> float:
        """Get minor radius.

        Returns:
            minor radius as const double.
        """
    def GetNormVector(self) -> Vector3D:
        """Get normvector.

        Returns:
            normvector as const Vector3D.
        """
    def GetOrigin(self) -> Point3D:
        """Get Origin.

        Returns:
            Point3D Origin
        """
    def GetPoint(self, angle: Angle) -> Point3D:
        """Get point on arc with given angle in world coordinates

        Args:
            angle: central angle of the point

        Returns:
            point on arc as Point3D.
        """
    def GetPointAngle(self, point: Point3D) -> Angle:
        """Get the angle of a point

        Args:
            point: Global point

        Returns:
            point angle
        """
    def GetPointRel(self, angle: Angle) -> Point3D:
        """Get point on arc with given angle in relative coordinates

        Args:
            angle: central angle of the point

        Returns:
            point on arc as Point3D.
        """
    def GetRefPlacement(self) -> AxisPlacement3D:
        """Get the reference placement

        Returns:
            reference placement
        """
    def GetRefPlacementRel(self) -> AxisPlacement3D:
        """Get the reference placement

        Returns:
            reference placement
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point

        Returns:
            reference point
        """
    def GetStartAngle(self) -> Angle:
        """Get start angle.

        Returns:
            angle as const Angle.
        """
    def GetStartPoint(self) -> Point3D:
        """Get start point in world coordinates

        Returns:
            start point
        """
    def GetStartRelPoint(self) -> Point3D:
        """Get start point in relative coordinates

        Returns:
            start point in relative coordinates
        """
    def GetXAxis(self) -> Vector3D:
        """Get Major axis (X-Axis of the placement).

        Returns:
            Major axis as const Vector3D.
        """
    def GetZAxis(self) -> Vector3D:
        """Get Normal vector of the placement.

        Returns:
            Normal vector as const Vector3D.
        """
    def IsAngleOnArc(self, angle: Angle) -> bool:
        """Checks if the given angle lies on the arc

        Args:
            angle: angle to test

        Returns:
            Angle on arc true/false
        """
    def IsCircle(self) -> bool:
        """Check if minor radius equals major radius

        Returns:
            result of check as bool.
        """
    def IsClockwise(self) -> bool:
        """Returns winding direction clockwise true/false

        Returns:
            Is winding direction clockwise true/false
        """
    def IsClosed(self) -> bool:
        """Check delta angle is 2pi

        Returns:
            result of check as bool.
        """
    def IsCounterClockwise(self) -> bool:
        """Returns winding direction counterclockwise true/false

        Returns:
            Is winding direction counterclockwise true/false
        """
    def IsEpsilonClosed(self) -> bool:
        """Check delta angle is 2pi

        Returns:
            result of check as bool.
        """
    def IsValid(self) -> bool:
        """Checks if the arc is valid

        Returns:
            Validity true/false
        """
    def Reverse(self):
        """Reverse of current arc

        Method reverse Arc, start with end angle and orientation.
        """
    def RotateAroundLocalZAxis(self, angle: Angle):
        """Rotate the arc around the Z-axis (normal vector)

        Args:
            angle: Rotation angle
        """
    def SetCenter(self, center: Point3D):
        """Set center point.

        Args:
            center: center point
        """
    def SetCenterRel(self, center: Point3D):
        """Set center point in local coordinate system

        Args:
            center: center point
        """
    @typing.overload
    def SetClockwise(self, cw: bool):
        """Set the winding direction of the arc

        Args:
            cw: winding clockwise true/false
        """
    @typing.overload
    def SetClockwise(self):
        """Set the winding direction of the arc to CW
        """
    def SetClockwise(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def SetCounterClockwise(self, ccw: bool):
        """Set the winding direction of the arc

        Args:
            ccw: winding counterclockwise true/false
        """
    @typing.overload
    def SetCounterClockwise(self):
        """Set the winding direction of the arc to CCW
        """
    def SetCounterClockwise(self):
        """ Overloaded function. See individual overloads.
        """
    def SetDeltaAngle(self, deltaAngle: Angle):
        """Set the delta angle.

        Set the delta angle

        Args:
            deltaAngle: angle which will be set.
        """
    @typing.overload
    def SetEndAngle(self, angle: Angle):
        """Set end angle.

        Set the end angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
        """
    @typing.overload
    def SetEndAngle(self, angle: Angle, ccw: bool):
        """Set end angle.

        Set the end angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
            ccw:   in counterclockwise winding
        """
    def SetEndAngle(self):
        """ Overloaded function. See individual overloads.
        """
    def SetEndPoint(self, endpoint: Point3D):
        """Set the end point of an object in world coordinates

        Args:
            endpoint: New end point of curve
        """
    def SetMajorRadius(self, radius: float):
        """Set major radius.

        Args:
            radius: major radius
        """
    def SetMinorRadius(self, radius: float):
        """Set minor radius.

        Args:
            radius: minor radius
        """
    def SetNormVector(self, normalVec: Vector3D):
        """Set the normvector

        Set the plane normal and normalizes it to unit vector

        Args:
            normalVec: Vector3D to be set
        """
    def SetOrigin(self, center: Point3D):
        """Set Origin

        Args:
            center: Origin
        """
    @typing.overload
    def SetRefPlacement(self, refPlacement: AxisPlacement3D):
        """Set the reference placement

        Args:
            refPlacement: reference placement
        """
    @typing.overload
    def SetRefPlacement(self, center: Point3D, xAxis: Vector3D, normalVec: Vector3D):
        """Set the reference placement

        Args:
            center:    center point
            xAxis:     X-axis of the arc
            normalVec: normal vector (Z-axis) of the arc
        """
    def SetRefPlacement(self):
        """ Overloaded function. See individual overloads.
        """
    def SetRefPlacementRel(self, refPlacement: AxisPlacement3D):
        """Set the reference placement relative to the refPoint

        Args:
            refPlacement: reference placement
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set the reference point

        Args:
            refPoint: reference point
        """
    @typing.overload
    def SetStartAngle(self, angle: Angle):
        """Set start angle

        Set the start angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
        """
    @typing.overload
    def SetStartAngle(self, angle: Angle, ccw: bool):
        """Set start angle.

        Set the start angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
            ccw:   in counterclockwise winding
        """
    def SetStartAngle(self):
        """ Overloaded function. See individual overloads.
        """
    def SetStartPoint(self, startpoint: Point3D):
        """Set the start point of an object in world coordinates

        Args:
            startpoint: New start point of curve
        """
    def __eq__(self, arc: Arc3D) -> bool:
        """Comparison of arcs.

        Be careful, this method work without tolerance!

        Args:
            arc: arc to be compared.

        Returns:
            True when arcs are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, arc: Arc3D):
        """Copy constructor.

        Args:
            arc: Arc3D which will be copied.
        """
    @typing.overload
    def __init__(self, center: Point3D, xDir: Vector3D, normVector: Vector3D, minor: float, major: float, startAngle: float,
                 deltaAngle: float):
        """Constructor

        Args:
            center:     Center point
            xDir:       X-axis
            normVector: Normal vector
            minor:      Minor radius
            major:      Major radius
            startAngle: Start angle
            deltaAngle: Delta angle
        """
    @typing.overload
    def __init__(self, center: Point3D, xDir: Vector3D, normVector: Vector3D, minor: float, major: float, startAngle: float,
                 endAngle: float, counterClockwise: bool):
        """Constructor

        Args:
            center:           Center point
            xDir:             X-axis
            normVector:       Normal vector
            minor:            Minor radius
            major:            Major radius
            startAngle:       Start angle
            endAngle:         End angle
            counterClockwise: Winding direction
        """
    @typing.overload
    def __init__(self, center: Point3D, minor: float, major: float, startAngle: float, deltaAngle: float):
        """Constructor

        Args:
            center:     Center point
            minor:      Minor radius
            major:      Major radius
            startAngle: Start angle
            deltaAngle: Delta angle
        """
    @typing.overload
    def __init__(self, center: Point3D, minor: float, major: float, startAngle: float, endAngle: float, counterClockwise: bool):
        """Constructor

        Args:
            center:           Center point
            minor:            Minor radius
            major:            Major radius
            startAngle:       Start angle
            endAngle:         End angle
            counterClockwise: Winding direction
        """
    @typing.overload
    def __init__(self, placement: AxisPlacement3D, minor: float, major: float, startAngle: float, deltaAngle: float):
        """Constructor

        Args:
            placement:  3D Placement
            minor:      Minor radius
            major:      Major radius
            startAngle: Start angle
            deltaAngle: Delta angle
        """
    @typing.overload
    def __init__(self, placement: AxisPlacement3D, minor: float, major: float, startAngle: float, endAngle: float, counterClockwise: bool):
        """Constructor

        Args:
            placement:        3D Placement
            minor:            Minor radius
            major:            Major radius
            startAngle:       Start angle
            endAngle:         End angle
            counterClockwise: Winding direction
        """
    @typing.overload
    def __init__(self, arc2D: Arc2D):
        """Constructor

        Args:
            arc2D: Arc to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Center(self) -> Point3D:
        """Get center.
        """
    @Center.setter
    def Center(self, center: Point3D) -> None:
        """Set center point.

        Args:
            center: center point
        """
    @property
    def CenterRel(self) -> Point3D:
        """Get center in relative coordinate system
        """
    @CenterRel.setter
    def CenterRel(self, center: Point3D) -> None:
        """Set center point in local coordinate system

        Args:
            center: center point
        """
    @property
    def CounterClockwise(self) -> bool:
        """Returns winding direction counterclockwise true/false
        """
    @CounterClockwise.setter
    def CounterClockwise(self, ccw: bool) -> None:
        """Returns winding direction counterclockwise true/false

        Set the winding direction of the arc

        Args:
            ccw: winding counterclockwise true/false
        """
    @property
    def DeltaAngle(self) -> Angle:
        """Get the delta angle
        """
    @DeltaAngle.setter
    def DeltaAngle(self, deltaAngle: Angle) -> None:
        """Set the delta angle.

        Set the delta angle

        Args:
            deltaAngle: angle which will be set.
        """
    @property
    def EndAngle(self) -> Angle:
        """Get end angle.
        """
    @EndAngle.setter
    def EndAngle(self, angle: Angle) -> None:
        """Set end angle.

        Set the end angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
        """
    @property
    def EndPoint(self) -> Point3D:
        """Get end point in world coordinates
        """
    @EndPoint.setter
    def EndPoint(self, endpoint: Point3D) -> None:
        """Set the end point of an object in world coordinates

        Args:
            endpoint: New end point of curve
        """
    @property
    def EndRelPoint(self) -> Point3D:
        """Get end point in relative coordinates
        """
    @property
    def MajorRadius(self) -> float:
        """Get major radius.
        """
    @MajorRadius.setter
    def MajorRadius(self, radius: float) -> None:
        """Set major radius.

        Args:
            radius: major radius
        """
    @property
    def MinorRadius(self) -> float:
        """Get minor radius.
        """
    @MinorRadius.setter
    def MinorRadius(self, radius: float) -> None:
        """Set minor radius.

        Args:
            radius: minor radius
        """
    @property
    def NormVector(self) -> Vector3D:
        """Get normvector.
        """
    @NormVector.setter
    def NormVector(self, normalVec: Vector3D) -> None:
        """Set the normvector

        Set the plane normal and normalizes it to unit vector

        Args:
            normalVec: Vector3D to be set
        """
    @property
    def Origin(self) -> Point3D:
        """Get Origin.
        """
    @Origin.setter
    def Origin(self, center: Point3D) -> None:
        """Set Origin

        Args:
            center: Origin
        """
    @property
    def RefPlacement(self) -> AxisPlacement3D:
        """Get the reference placement
        """
    @RefPlacement.setter
    def RefPlacement(self, refPlacement: AxisPlacement3D) -> None:
        """Set the reference placement

        Args:
            refPlacement: reference placement
        """
    @property
    def RefPlacementRel(self) -> AxisPlacement3D:
        """Get the reference placement
        """
    @RefPlacementRel.setter
    def RefPlacementRel(self, refPlacement: AxisPlacement3D) -> None:
        """Set the reference placement relative to the refPoint

        Args:
            refPlacement: reference placement
        """
    @property
    def RefPoint(self) -> Point3D:
        """Get the reference point
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point3D) -> None:
        """Set the reference point

        Args:
            refPoint: reference point
        """
    @property
    def StartAngle(self) -> Angle:
        """Get start angle.
        """
    @StartAngle.setter
    def StartAngle(self, angle: Angle) -> None:
        """Set start angle

        Set the start angle and normalize it to [0,2PI[

        Args:
            angle: angle which will be set.
        """
    @property
    def StartPoint(self) -> Point3D:
        """Get start point in world coordinates
        """
    @StartPoint.setter
    def StartPoint(self, startpoint: Point3D) -> None:
        """Set the start point of an object in world coordinates

        Args:
            startpoint: New start point of curve
        """
    @property
    def StartRelPoint(self) -> Point3D:
        """Get start point in relative coordinates
        """

class Arc3DList():
    """List for Arc3D objects
    """
    def __contains__(self, value: Arc3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Arc3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Arc3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Arc3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Arc3DList:
        """Add a list

        Args:
            eleList: Arc3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Arc3D):
        """Constructor with a Arc3D

        Args:
            ele: Arc3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Arc3D

        Args:
            eleList: Arc3D list
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
    def __setitem__(self, index: (int | slice), value: Arc3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Arc3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Arc3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Arc3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Axis2D():
    """Representation class for 2D Axis
    """
    def GetAxisPoint(self) -> Point2D:
        """Get axis point in world coordinate system.

        Returns:
            Axis point in world coordinates
        """
    def GetAxisPoint2(self) -> Point2D:
        """Get second axis point. Used world coordinate system.

        Returns:
            Second axis point in world coordinates
        """
    def GetAxisRelPoint(self) -> Point2D:
        """Get axis point in local coordinate system

        Returns:
            Axis point in local coordinates
        """
    def GetAxisRelPoint2(self) -> Point2D:
        """Get second axis point. Used local coordinate system

        Returns:
            Second axis point in local coordinates
        """
    def GetRefPoint(self) -> Point2D:
        """Get reference point.

        Returns:
            Reference point
        """
    def GetVector(self) -> Vector2D:
        """Get axis vector

        Returns:
            Axis vector
        """
    @typing.overload
    def Set(self, axis: Axis2D):
        """Set axis

        Args:
            axis: Axis which will be copied
        """
    @typing.overload
    def Set(self, refPoint: Point2D, axisPoint: Point2D, vector: Vector2D):
        """Set axis

        Used local coordinate system for axisPoint

        Args:
            refPoint:  Reference point
            axisPoint: Axis point
            vector:    Axis vector
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetAxisPoint(self, point: Point2D):
        """Set axis point, used world coordinate system.

        Args:
            point: Axis point in world coordinates
        """
    def SetAxisRelPoint(self, axisPoint: Point2D):
        """Set axis point, used local coordinate system.

        Args:
            axisPoint: Axis point in local coordinates
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set reference point

        Args:
            refPoint: New reference point
        """
    def SetVector(self, vector: Vector2D):
        """Set axis vector

        Args:
            vector: New axis vector
        """
    def __eq__(self, axis: Axis2D) -> bool:
        """Comparison of axes.

        Be careful, this method work without tolerance!

        Args:
            axis: axis to be compared.

        Returns:
            True when axes are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, axis: Axis2D):
        """Copy constructor.

        Args:
            axis: Axis which will be copied
        """
    @typing.overload
    def __init__(self, axisPoint: Point2D, vector: Vector2D):
        """Constructor.

        Reference point is initialized to [0.,0.]
        Used world coordinate system for AxisPoint

        Args:
            axisPoint: Axis point
            vector:    Axis vector
        """
    @typing.overload
    def __init__(self, refPoint: Point2D, axisPoint: Point2D, vector: Vector2D):
        """Constructor.

        Used local coordinate system for AxisPoint

        Args:
            refPoint:  Reference point
            axisPoint: Axis point
            vector:    Axis vector
        """
    @typing.overload
    def __init__(self, line: Line2D):
        """Explicit constructor from Line2D

        Args:
            line: 2D line
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def AxisPoint(self) -> Point2D:
        """Get axis point in world coordinate system.
        """
    @AxisPoint.setter
    def AxisPoint(self, point: Point2D) -> None:
        """Set axis point, used world coordinate system.

        Args:
            point: Axis point in world coordinates
        """
    @property
    def AxisRefPoint(self) -> Point2D:
        """Get reference point.
        """
    @AxisRefPoint.setter
    def AxisRefPoint(self, refPoint: Point2D) -> None:
        """Set reference point

        Args:
            refPoint: New reference point
        """
    @property
    def AxisRelPoint(self) -> Point2D:
        """Get axis point in local coordinate system
        """
    @AxisRelPoint.setter
    def AxisRelPoint(self, axisPoint: Point2D) -> None:
        """Set axis point, used local coordinate system.

        Args:
            axisPoint: Axis point in local coordinates
        """
    @property
    def AxisVector(self) -> Vector2D:
        """Get axis vector
        """
    @AxisVector.setter
    def AxisVector(self, vector: Vector2D) -> None:
        """Set axis vector

        Args:
            vector: New axis vector
        """

class Axis3D():
    """Representation class for 3D Axis
    """
    def GetAxisPoint(self) -> Point3D:
        """Get axis point in world coordinate system.

        Returns:
            Axis point in world coordinates
        """
    def GetAxisPoint2(self) -> Point3D:
        """Get second axis point. Used world coordinate system.

        Returns:
            Second axis point in world coordinates
        """
    def GetAxisRelPoint(self) -> Point3D:
        """Get axis point in local coordinate system

        Returns:
            Axis point in local coordinates
        """
    def GetAxisRelPoint2(self) -> Point3D:
        """Get second axis point. Used local coordinate system

        Returns:
            Second axis point in local coordinates
        """
    def GetRefPoint(self) -> Point3D:
        """Get reference point.

        Returns:
            Reference point
        """
    def GetVector(self) -> Vector3D:
        """Get axis vector

        Returns:
            Axis vector
        """
    @typing.overload
    def Set(self, axis: Axis3D):
        """Set axis

        Args:
            axis: Axis which will be copied
        """
    @typing.overload
    def Set(self, refPoint: Point3D, axisPoint: Point3D, vector: Vector3D):
        """Set axis

        Used local coordinate system for axisPoint

        Args:
            refPoint:  Reference point
            axisPoint: Axis point
            vector:    Axis vector
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetAxisPoint(self, point: Point3D):
        """Set axis point, used world coordinate system.

        Args:
            point: Axis point in world coordinates
        """
    def SetAxisRelPoint(self, axisPoint: Point3D):
        """Set axis point, used local coordinate system.

        Args:
            axisPoint: Axis point in local coordinates
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set reference point

        Args:
            refPoint: New reference point
        """
    def SetVector(self, vector: Vector3D):
        """Set axis vector

        Args:
            vector: New axis vector
        """
    def __eq__(self, axis: Axis3D) -> bool:
        """Comparison of axes.

        Be careful, this method work without tolerance!

        Args:
            axis: axis to be compared.

        Returns:
            True when axes are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, axis: Axis3D):
        """Copy constructor.

        Args:
            axis: Axis which will be copied
        """
    @typing.overload
    def __init__(self, axisPoint: Point3D, vector: Vector3D):
        """Constructor.

        Reference point is initialized to [0.,0.,0.]
        Used world coordinate system for AxisPoint

        Args:
            axisPoint: Axis point
            vector:    Axis vector
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, axisPoint: Point3D, vector: Vector3D):
        """Constructor.

        Used local coordinate system for AxisPoint

        Args:
            refPoint:  Reference point
            axisPoint: Axis point
            vector:    Axis vector
        """
    @typing.overload
    def __init__(self, line: Line3D):
        """Constructor

        Args:
            line: 3D line representing axis
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def AxisPoint(self) -> Point3D:
        """Get axis point in world coordinate system.
        """
    @AxisPoint.setter
    def AxisPoint(self, point: Point3D) -> None:
        """Set axis point, used world coordinate system.

        Args:
            point: Axis point in world coordinates
        """
    @property
    def AxisRefPoint(self) -> Point3D:
        """Get reference point.
        """
    @AxisRefPoint.setter
    def AxisRefPoint(self, refPoint: Point3D) -> None:
        """Set reference point

        Args:
            refPoint: New reference point
        """
    @property
    def AxisRelPoint(self) -> Point3D:
        """Get axis point in local coordinate system
        """
    @AxisRelPoint.setter
    def AxisRelPoint(self, axisPoint: Point3D) -> None:
        """Set axis point, used local coordinate system.

        Args:
            axisPoint: Axis point in local coordinates
        """
    @property
    def AxisVector(self) -> Vector3D:
        """Get axis vector
        """
    @AxisVector.setter
    def AxisVector(self, vector: Vector3D) -> None:
        """Set axis vector

        Args:
            vector: New axis vector
        """

class AxisPlacement2D():
    """Representation class for orthogonal axis placement

    Placement is given by reference point and direction vector of local x-axis
    """
    def GetDirection(self) -> Vector2D:
        """Get direction

        Returns:
            Vector2D const reference
        """
    def GetRefPoint(self) -> Point2D:
        """Get the reference point

        Returns:
            Reference point
        """
    def GetYDirection(self) -> Vector2D:
        """Get direction of local y-axis

        Returns:
            Vector2D const reference
        """
    def IsValid(self) -> bool:
        """Check if the placement is valid

        Returns:
            True if it is a valid placement
        """
    def SetDirection(self, dir: Vector2D):
        """Set direction

        Args:
            dir: Vector2D const reference
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set reference point

        Args:
            refPoint: New reference point
        """
    def __eq__(self, axis_placement: AxisPlacement2D) -> bool:
        """Comparison of axis placements.

        Be careful, this method work without tolerance!

        Args:
            axis_placement: axis placement to be compared.

        Returns:
            True when axis placements are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: AxisPlacement2D):
        """Copy constructor.

        Args:
            placement: Extruded area placement which will be copied
        """
    @typing.overload
    def __init__(self, refPoint: Point2D, dirvector: Vector2D):
        """Constructor which fully constructs the element.

        Args:
            refPoint:  reference point
            dirvector: direction vector
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Direction(self) -> Vector2D:
        """Get direction
        """
    @Direction.setter
    def Direction(self, dir: Vector2D) -> None:
        """Set direction

        Args:
            dir: Vector2D const reference
        """
    @property
    def RefPoint(self) -> Point2D:
        """Get the reference point
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point2D) -> None:
        """Set reference point

        Args:
            refPoint: New reference point
        """

class AxisPlacement2DList():
    """List for AxisPlacement2D objects
    """
    def __contains__(self, value: AxisPlacement2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: AxisPlacement2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: AxisPlacement2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> AxisPlacement2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> AxisPlacement2DList:
        """Add a list

        Args:
            eleList: AxisPlacement2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: AxisPlacement2D):
        """Constructor with a AxisPlacement2D

        Args:
            ele: AxisPlacement2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of AxisPlacement2D

        Args:
            eleList: AxisPlacement2D list
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
    def __setitem__(self, index: (int | slice), value: AxisPlacement2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: AxisPlacement2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: AxisPlacement2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: AxisPlacement2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class AxisPlacement3D():
    """Representation class for orthogonal axis placement in 3D space

    Placement is given by Origin and 2 direction vectors - local x-axis
    and local z-axis. y-axis is computed on demand
    """
    def CalcGlobalPoint(self, point: Point3D) -> Point3D:
        """Calculate global point from local coordinate system of placement 3D

        Args:
            point: local point 3D

        Returns:
            Point3D instance
        """
    def CalcLocalPoint(self, point: Point3D) -> Point3D:
        """Calculate local point in coordinate system of placement 3D

        Args:
            point: global point 3D

        Returns:
            Point3D instance
        """
    def GetOrigin(self) -> Point3D:
        """Get origin

        Returns:
            Origin
        """
    def GetRotationMatrix(self) -> Matrix3D:
        """Get Rotation matrix given by placement 3D

        Returns:
            Matrix3D const reference
        """
    def GetTransformationMatrix(self) -> Matrix3D:
        """Get Transformation matrix given by placement 3D

        Returns:
            Matrix3D const reference
        """
    def GetXDirection(self) -> Vector3D:
        """Get x-direction

        Returns:
            Vector3D const reference
        """
    def GetYDirection(self) -> Vector3D:
        """Get direction of local y-axis

        Returns:
            Vector3D const reference
        """
    def GetZDirection(self) -> Vector3D:
        """Get z-direction

        Returns:
            Vector3D const reference
        """
    def IsValid(self) -> bool:
        """Check if the placement is valid

        Returns:
            True if it is a valid placement
        """
    def RotateAroundLocalZAxis(self, angle: Angle):
        """Rotate the placement around it's Z-axis

        Args:
            angle: rotation angle
        """
    def Set(self, origin: Point3D, xDir: Vector3D, zDir: Vector3D):
        """Set the placement

        Args:
            origin: New origin
            xDir:   New X-direction
            zDir:   New Z-direction
        """
    def SetOrigin(self, origin: Point3D):
        """Set origin

        Args:
            origin: New origin
        """
    def SetXDirection(self, dir: Vector3D):
        """Set x-direction

        Args:
            dir: Vector3D const reference
        """
    def SetZDirection(self, dir: Vector3D):
        """Set z-direction

        Args:
            dir: Vector3D const reference
        """
    def __eq__(self, axis_placement: AxisPlacement3D) -> bool:
        """Comparison of axis placements.

        Be careful, this method work without tolerance!

        Args:
            axis_placement: axis placement to be compared.

        Returns:
            True when axis placements are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, placement: AxisPlacement3D):
        """Copy constructor.

        Args:
            placement: Placement to be copied
        """
    @typing.overload
    def __init__(self, refPoint: Point3D):
        """Constructor with only reference point

        Args:
            refPoint: reference point
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, xvector: Vector3D, zvector: Vector3D):
        """Constructor which fully constructs the element.

        Args:
            refPoint: reference point
            xvector:  direction vector X
            zvector:  direction vector Z
        """
    @typing.overload
    def __init__(self, rotationAxis: Axis3D, rotationStart: Point3D):
        """Constructor from rotation axis and start point of rotation.

        Args:
            rotationAxis:  rotation axis
            rotationStart: starting point of rotation, have not to be on axis
        """
    @typing.overload
    def __init__(self, matrix: Matrix3D):
        """Constructor from Matrix3D

        Args:
            matrix: matrix
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Origin(self) -> Point3D:
        """Get origin
        """
    @Origin.setter
    def Origin(self, origin: Point3D) -> None:
        """Set origin

        Args:
            origin: New origin
        """
    @property
    def XDirection(self) -> Vector3D:
        """Get x-direction
        """
    @XDirection.setter
    def XDirection(self, dir: Vector3D) -> None:
        """Set x-direction

        Args:
            dir: Vector3D const reference
        """
    @property
    def ZDirection(self) -> Vector3D:
        """Get z-direction
        """
    @ZDirection.setter
    def ZDirection(self, dir: Vector3D) -> None:
        """Set z-direction

        Args:
            dir: Vector3D const reference
        """

class AxisPlacement3DList():
    """List for AxisPlacement3D objects
    """
    def __contains__(self, value: AxisPlacement3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: AxisPlacement3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: AxisPlacement3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> AxisPlacement3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> AxisPlacement3DList:
        """Add a list

        Args:
            eleList: AxisPlacement3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: AxisPlacement3D):
        """Constructor with a AxisPlacement3D

        Args:
            ele: AxisPlacement3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of AxisPlacement3D

        Args:
            eleList: AxisPlacement3D list
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
    def __setitem__(self, index: (int | slice), value: AxisPlacement3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: AxisPlacement3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: AxisPlacement3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: AxisPlacement3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class BRep3D():
    """Representation class for 3D boundary representation.
    """
    def AreFacesNaturallyTrimmed(self) -> bool:
        """Find if all faces are naturally trimmed by their surfaces

        throw Exception in case of invalid object.

        Returns:
            bool (true = yes)
        """
    @staticmethod
    def CreateCone(cone: Cone3D, closed: bool = True) -> BRep3D:
        """Create BRep3D as cone

        Args:
            cone:   cone data
            closed: whether to create solid or sheet body

        Returns:
            created geometry
        """
    @staticmethod
    def CreateCuboid(placement: AxisPlacement3D, length: float, width: float, height: float) -> BRep3D:
        """Create BRep3D as cuboid

        Args:
            placement: cuboid origin
            length:    length in its x axis
            width:     width in its y axis
            height:    height in its z axis

        Returns:
            created geometry
        """
    @staticmethod
    def CreateCylinder(placement: AxisPlacement3D, radius: float, height: float, closedTop: bool = True,
                       closedBottom: bool = True) -> BRep3D:
        """Create Brep as cylinder

        Args:
            placement:    axis placement
            radius:       cylinder radius
            height:       cylinder height
            closedTop:    whether to close top of cylinder
            closedBottom: whether to close bottom of cylinder

        Returns:
            created cone
        """
    @staticmethod
    def CreateSphere(placement: AxisPlacement3D, radius: float) -> BRep3D:
        """Create BRep3D as sphere

        Args:
            placement: sphere origin
            radius:    sphere radius

        Returns:
            created geometry
        """
    @staticmethod
    def CreateWireBody(icurve: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D) -> BRep3D:
        """Create wire body from the curve as one edge

        Args:
            icurve: curve for edge geometry

        Returns:
            created BRep3D element
        """
    def DeleteFace(self, faceIndex: int) -> eGeometryErrorCode:
        """Delete face from brep

        Args:
            faceIndex: index of face we want to delete

        Returns:
            error code
        """
    def DeleteFaces(self, faceIndices: NemAll_Python_Utility.VecULongList) -> eGeometryErrorCode:
        """Delete faces from brep

        Args:
            faceIndices: indices of faces to delete

        Returns:
            error code
        """
    def GetAllEdgesFlags(self) -> tuple[eGeometryErrorCode, list[int]]:
        """Get flags of the all edges.

        Returns:
            tuple(Error code,
                  flags values)
        """
    def GetAllFacesFlags(self) -> tuple[eGeometryErrorCode, list[int]]:
        """Get flags of the all faces.

        Returns:
            tuple(Error code,
                  flags values)
        """
    def GetEdgeCount(self) -> int:
        """Get the edges count

        Returns:
            size_t count of edges
        """
    def GetEdgeCurves(self) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """get all edge curves as BSpline3D

        Returns:
            tuple(error code,
                  result edge curves handle vector)
        """
    def GetEdgeFaceIndices(self, edge: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get faces containing this edge (if any)

        Args:
            edge: desired edge index

        Returns:
            tuple(error code,
                  face indices)
        """
    def GetEdgeGeometry(self, edge: int) -> typing.Any:
        """Get (trimmed) edge geometry as BSpline3D

        Args:
            edge: edge index

        Returns:
            handle to geometry curve
        """
    def GetEdgeParametricCurves(self) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """get parametric curves of all edges

        Returns:
            tuple(error code,
                  result edge curves handle vector)
        """
    def GetEdgeParametricGeometry(self, edge: int) -> typing.Any:
        """Get (trimmed) edge geometry as parametric curves

        Args:
            edge: edge index

        Returns:
            handle to geometry curve
        """
    def GetEdgeVertexIndices(self, edge: int) -> tuple:
        """Get vertex indices of the edge

        Args:
            edge: edge index

        Returns:
             error code,
             start vertex index,
             end vertex index
        """
    def GetEdgeVertices(self, edge: int) -> tuple[eGeometryErrorCode, Point3D, Point3D]:
        """get edge vertices

        Args:
            edge: edge index

        Returns:
            tuple(error code,
                  start vertex,
                  end vertex)
        """
    def GetExactTypeIsoCurves(self, ucount: int, vcount: int, planarfaces: bool = False) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """Get iso curves from all faces

        Args:
            ucount:      number of u-curves
            vcount:      number of v-curves
            planarfaces: include planar faces

        Returns:
            tuple(error code,
                  result iso curves handle vector)
        """
    def GetFaceBoundaryCurves(self, face: int) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """Get face boundary curves, curves are trimmed

        Args:
            face: face index

        Returns:
            tuple(error code,
                  result geometries)
        """
    def GetFaceCount(self) -> int:
        """Get the faces count

        Returns:
            size_t count of faces
        """
    def GetFaceEdgeNaturalTrimming(self, face: int, oedge: OrientedEdge) -> tuple[eGeometryErrorCode, eSurfaceTrimParam]:
        """get edge trimming on this face

        Args:
            face:  face index
            oedge: oriented edge

        Returns:
            tuple(error code,
                  result trimming)
        """
    def GetFaceEdgeOrientation(self, face: int, edge: int) -> tuple[eGeometryErrorCode, bool]:
        """Get orientation of the edge in the given face

        Args:
            face: face index
            edge: edge index

        Returns:
            tuple(error code,
                  result orientation (same = true or opposite = false))
        """
    def GetFaceEdges(self, faceIndex: int) -> tuple[eGeometryErrorCode, list[OrientedEdge]]:
        """Get face edges together with their orientations

        Args:
            faceIndex: face index

        Returns:
            tuple(error code,
                  result edges)
        """
    def GetFaceFlags(self, face: int) -> int:
        """Get flags of the face.

        Args:
            face: face index

        Returns:
            flags value
        """
    def GetFaceGeometry(self, face: int) -> typing.Any:
        """Get surface geometry of the face

        throw Exception in case of invalid input.

        Args:
            face: face index

        Returns:
            surface geometry handle
        """
    def GetFaceGeometryOrientation(self, face: int) -> bool:
        """Get surface geometry orientation of the face

        Args:
            face: face index

        Returns:
            surface geometry orientation
        """
    def GetFaceLoops(self, face: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get loops from given face

        Args:
            face: face to find loops

        Returns:
            tuple(error code,
                  face loops indices)
        """
    def GetFaceLoopsCount(self, face: int) -> int:
        """Get count of loops of face given by index

        Args:
            face: index of face

        Returns:
            count of loops
        """
    def GetFaceUVBox(self, face: int) -> tuple[eGeometryErrorCode, MinMax2D]:
        """Get uv box of the face

        Args:
            face: selected face

        Returns:
            tuple(error code,
                  uv box of face)
        """
    def GetFaceVerticesIndices(self, faceIndex: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get indices of vertices for given face index

        Args:
            faceIndex: index of face

        Returns:
            tuple(error code,
                  indices of vertices)
        """
    def GetFinData(self, fin: int) -> tuple[eGeometryErrorCode, int, bool]:
        """Get index of edge to which fin belongs and its sense

        Args:
            fin: fin to find infos

        Returns:
            tuple(error code,
                  index of edge to which fin belongs,
                  fin sense)
        """
    def GetIsoCurves(self, ucount: int, vcount: int, planarfaces: bool = False) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """Get iso curves from all faces

        Args:
            ucount:      number of u-curves
            vcount:      number of v-curves
            planarfaces: include planar faces

        Returns:
            tuple(error code,
                  result iso curves handle vector)
        """
    def GetLoopFins(self, loop: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get fins from given loop

        Args:
            loop: loop to find fins

        Returns:
            tuple(error code,
                  loop fins indices)
        """
    def GetParts(self) -> tuple[eGeometryErrorCode, list[BRep3D]]:
        """Get separated parts (continuos shells)

        Returns:
            tuple(error code,
                  separated bodies)
        """
    def GetPartsCount(self) -> int:
        """Get number of parts in this body

        Returns:
            number of parts
        """
    def GetPlanarFaces(self) -> list[tuple[Plane3D, int]]:
        """Get planar faces if this brep contains planar faces

        Returns:
            pairs of - surface geometry and surface index
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point

        Returns:
            Constant reference point.
        """
    def GetSilhouetteCurves(self, viewMatrix: Matrix3D, bPerspective: bool) -> tuple[eGeometryErrorCode, list[typing.Any]]:
        """Get silhouette curves of Brep

        Args:
            viewMatrix:   View matrix
            bPerspective: Flag if it is central projection or not (true / false)

        Returns:
            tuple(error code,
                  silhouette curves)
        """
    def GetSilhouetteVertices(self, viewMatrix: Matrix3D, bPerspective: bool) -> tuple[eGeometryErrorCode, list[Point3D]]:
        """Get vertices (end points) of silhouette curves

        Args:
            viewMatrix:   view matrix
            bPerspective: Flag if view is central perspective (true / false)

        Returns:
            tuple(error code,
                  output vector of found points)
        """
    def GetVertex(self, vertexIndex: int) -> tuple[eGeometryErrorCode, Point3D]:
        """Get vertex geometry

        Args:
            vertexIndex: vertex index

        Returns:
            tuple(error code,
                  vertex point)
        """
    def GetVertexCount(self) -> int:
        """Get the vertices count

        Returns:
            count of vertices
        """
    def GetVertexEdges(self, vertex: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get the edges containing given vertex

        Args:
            vertex: Index of vertex

        Returns:
            tuple(Error code,
                  Indices of edges that contains vertex)
        """
    def GetVertexFaceIndices(self, vertexIndex: int) -> tuple[eGeometryErrorCode, list[int]]:
        """Get indices of faces for given vertex index

        Args:
            vertexIndex: index of vertex

        Returns:
            tuple(error code,
                  indices of faces)
        """
    def GetVertices(self) -> tuple[eGeometryErrorCode, list[Point3D]]:
        """Get all vertices from brep

        Returns:
            tuple(error code,
                  vertices of brep)
        """
    def GetVirtualVertices(self) -> tuple[eGeometryErrorCode, list[Point3D], list[int]]:
        """Get vertices from edges without vertex (get start points of edge curves)

        Returns:
            tuple(error code,
                  points (start points of curves),
                  indices of edges without real vertex)
        """
    def GetVirtualVerticesCount(self) -> int:
        """Get count of vertices (count of edges without vertex)

        Returns:
            count of vertices (edges without vertex)
        """
    def HasPlanarFaces(self) -> bool:
        """Check if this brep contains planar faces

        Returns:
            bool true = yes
        """
    def InvertAllEdgesFlags(self):
        """Invert flags for the all edges
        """
    def InvertAllFacesFlags(self):
        """Invert flags for the all faces
        """
    def IsClosed(self) -> bool:
        """Check whether the B-rep is closed (closed shells)

        Returns:
            bool true = yes
        """
    def IsCone(self) -> tuple[bool, AxisPlacement3D, float, float, float]:
        """Check if the b-rep is a cone

        Returns:
            tuple(bool true = yes,
                  result axis placement (cone bottom center, axis orientation),
                  cone bottom radius,
                  cone top radius,
                  cone height)
        """
    def IsEmpty(self) -> bool:
        """Returns true if the body is empty

        Returns:
            bool
        """
    def IsFaceNaturallyTrimmed(self, face: int) -> bool:
        """Find if the face is naturally trimmed by its surface

        throw Exception in case of invalid input.

        Args:
            face: face index

        Returns:
            bool (true = yes)
        """
    def IsPolyhedron(self) -> bool:
        """Check if the b-rep is a polyhedron

        Returns:
            bool true = yes
        """
    def IsSphere(self) -> tuple[bool, AxisPlacement3D, float]:
        """Check if the b-rep is a sphere

        Returns:
            tuple(bool true = yes,
                  result axis placement (sphere center, axis orientation),
                  sphere radius)
        """
    def IsValid(self) -> bool:
        """check whether data is valid

        Returns:
            bool true = is valid
        """
    def IsWire(self) -> bool:
        """Check if BRep is wire body. If has only edges.

        Returns:
            true if BRep is wire.
        """
    def PickEdge(self, rayPoint: Point3D, rayVector: Vector3D, searchRadius: float) -> tuple[bool, int, float, Point3D]:
        """Pick the edge under cursor

        Args:
            rayPoint:     ray point
            rayVector:    ray vector
            searchRadius: search radius

        Returns:
            tuple(true if any edge under cursor found,
                  index of found edge,
                  minimal distance between edge and ray,
                  nearest point on ray from edge)
        """
    def PickEdges(self, rayPoint: Point3D, rayVector: Vector3D, searchRadius: float) -> tuple[bool, list[int], list[float], list[Point3D]]:
        """Pick the edges under cursor

        Args:
            rayPoint:     ray point
            rayVector:    ray vector
            searchRadius: search radius

        Returns:
            tuple(true if any edge under cursor found,
                  index of found edge,
                  minimal distance between edge and ray,
                  nearest point on ray from edge)
        """
    def PickFace(self, rayPoint: Point3D, rayVector: Vector3D) -> tuple[bool, int, Point3D]:
        """Pick the face under cursor

        Args:
            rayPoint:  ray point
            rayVector: ray vector

        Returns:
            tuple(true if any face under cursor found,
                  index of found face,
                  nearest point on ray from face (intersection point))
        """
    def PickVertex(self, rayPoint: Point3D, rayVector: Vector3D, searchRadius: float) -> tuple[bool, int, float, Point3D]:
        """Pick the vertex under cursor

        Args:
            rayPoint:     ray point
            rayVector:    ray vector
            searchRadius: search radius

        Returns:
            tuple(true if any vertex under cursor found,
                  index of found vertex,
                  minimal distance between vertex and ray,
                  nearest point on ray from vertex)
        """
    @typing.overload
    def ReadFromStream(self, sstream_str: str, transformationMatrix: Matrix3D) -> eGeometryErrorCode:
        """Read BRep3D from string

        Args:
            sstream_str:          input string
            transformationMatrix: Matrix to use for BRep transformation

        Returns:
            error code
        """
    @typing.overload
    def ReadFromStream(self, sstream_str: str, scale: float, translation: Vector3D, spaceminmax: MinMax3D,
                       visibleminmax: MinMax3D) -> eGeometryErrorCode:
        """Read BRep3D from the string

        Args:
            sstream_str:   string to read brep data from
            scale:         transformation scale
            translation:   translation vector
            spaceminmax:   space minmax (including control points
            visibleminmax: visible minmax of the body

        Returns:
            error code
        """
    def ReadFromStream(self):
        """ Overloaded function. See individual overloads.
        """
    def Reverse(self) -> eGeometryErrorCode:
        """Reverse the orientation of BRep

        Returns:
            error code
        """
    def SetAllEdgesFlags(self, flags: int):
        """Set flags to the all edges.

        Args:
            flags: flags value
        """
    def SetAllFacesFlags(self, flags: int):
        """Set flags to the all faces.

        Args:
            flags: flags value
        """
    def SetFaceFlags(self, face: int, flags: int):
        """Set flags to the face.

        Args:
            face:  face index
            flags: flags value
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set the reference point

        Args:
            refPoint: New reference point.
        """
    def WriteToStream(self) -> tuple[eGeometryErrorCode, str, Matrix3D]:
        """Write BRep3D to the text

        Returns:
            tuple(error code,
                  output string,
                  Matrix used to transform BRep)
        """
    def WriteToStreamSplitTransform(self) -> tuple[eGeometryErrorCode, str, float, Vector3D, MinMax3D, MinMax3D]:
        """Write BRep3D to the text, get transform parameters and minmax

        Returns:
            tuple(error code,
                  output string,
                  transform scale,
                  translation vector,
                  space minmax (including control points),
                  visible minmax of the body)
        """
    def __eq__(self, brep: BRep3D) -> object:
        """Comparison of breps without tolerance.

        Be careful, this method work without tolerance!

        Args:
            brep:Compared brep.

        Returns:
            True when breps are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, brep: BRep3D):
        """Copy constructor

        Args:
            brep: BRep3D which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def AllEdgesFlags(self) -> eGeometryErrorCode:
        """Get flags of the all edges.
        """
    @AllEdgesFlags.setter
    def AllEdgesFlags(self, flags: eGeometryErrorCode) -> None:
        """Set flags to the all edges.

        Args:
            flags: flags value
        """
    @property
    def AllFacesFlags(self) -> eGeometryErrorCode:
        """Get flags of the all faces.
        """
    @AllFacesFlags.setter
    def AllFacesFlags(self, flags: eGeometryErrorCode) -> None:
        """Set flags to the all faces.

        Args:
            flags: flags value
        """
    @property
    def RefPoint(self) -> Point3D:
        """Get the reference point
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point3D) -> None:
        """Set the reference point

        Args:
            refPoint: New reference point.
        """

class BRep3DBuilder():
    """Builder for BRep3D
    """
    @typing.overload
    def AddEdge(self, edgeIdx: int, edgeSense: bool, loopIdx: int) -> bool:
        """Add edge to loop

        Args:
            edgeIdx:   Index of already added edge
            edgeSense: Sense of edge
            loopIdx:   Index of loop to which edge will be added
        """
    @typing.overload
    def AddEdge(self, curve: object, curveSense: bool, edgeSense: bool, loopIdx: int, precision: float) -> int:
        """Add edge to loop

        Args:
            curve:      Geometry of curve
            curveSense: Sense of curve
            edgeSense:  Sense of edge
            loopIdx:    Index of loop to which edge will be added
            precision:  Precision of edge

        Returns:
            Index of edge
        """
    def AddEdge(self):
        """ Overloaded function. See individual overloads.
        """
    def AddFace(self, surface: object, sense: bool) -> int:
        """Add face

        Args:
            surface: Geometry of surface
            sense:   Sense of surface

        Returns:
            Index of face
        """
    def AddLoop(self, faceIdx: int) -> int:
        """Add loop

        Args:
            faceIdx: Index of face to which loop will be added

        Returns:
            Index of face
        """
    @typing.overload
    def AddVertex(self, point: Point3D, edgeIdx: int, precision: float) -> int:
        """Add vertex to edge

        Args:
            point:     Geometry point
            edgeIdx:   Index of edge to which vertex will be added
            precision: Vertex precision

        Returns:
            Index of vertex
        """
    @typing.overload
    def AddVertex(self, vertexIdx: int, edgeIdx: int) -> bool:
        """Add vertex to edge

        Args:
            vertexIdx: Index of already added vertex
            edgeIdx:   Index of edge to which vertex will be added
        """
    def AddVertex(self):
        """ Overloaded function. See individual overloads.
        """
    def CheckLoop(self, loopIdx: int) -> bool:
        """Check whether loop topology is correct

        Args:
            loopIdx: Index of loop to check

        Returns:
            Flag whether loop is topologically correct
        """
    def Complete(self) -> BRep3D:
        """Complete topology and create BRep

        Returns:
            Created BRep
        """
    def Init(self, isSolid: bool):
        """Add body, region and shell

        Args:
            isSolid: Flag whether body is solid
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, element: BRep3DBuilder):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class BRep3DList():
    """List for BRep3D objects
    """
    def __contains__(self, value: BRep3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BRep3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BRep3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BRep3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BRep3DList:
        """Add a list

        Args:
            eleList: BRep3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BRep3D):
        """Constructor with a BRep3D

        Args:
            ele: BRep3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BRep3D

        Args:
            eleList: BRep3D list
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
    def __setitem__(self, index: (int | slice), value: BRep3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BRep3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BRep3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BRep3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class PolyPoints2D():
    """The PolyPoints class is the base template class for all objects which store geometry as a vector of points (or another objects), specially for polyline, polygon and spline.
    """
    def Clear(self):
        """Remove all points from vector.
        """
    def Count(self) -> int:
        """Get count of points.

        Returns:
            bool.
        """
    def Empty(self) -> bool:
        """Return true if no points, otherwise false.

        Returns:
            bool.
        """
    def EqualRef(self, polyPoints: PolyPoints2D) -> bool:
        """Test if reference points are equal.

        Args:
            polyPoints: constant the PolyPoints.

        Returns:
            Reference points are equal: true/false
        """
    def GetEndPoint(self) -> Point2D:
        """Get the end point in world coordinate system.

        Returns:
            end point in world coordinate system
        """
    def GetEndRelPoint(self) -> Point2D:
        """Get the end point

        Returns:
            end point
        """
    def GetLastPoint(self) -> Point2D:
        """Get the last point in world coordinate system, data.

        Returns:
            last point in world coordinate system
        """
    def GetPoint(self, index: int) -> Point2D:
        """Get point in world coordinate system, data.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point point in world coordinate system.
        """
    def GetPointIndex(self, point: Point2D) -> tuple[bool, int]:
        """Get index of the given point

        Args:
            point: Searched point

        Returns:
            tuple(True if a point was found,
                  Found index)
        """
    def GetPointIndexes(self, point: Point2D) -> tuple[bool, list[int]]:
        """Get indexes of the given point, in case that several points in the spline
        will have the same coordinates

        Args:
            point: Searched point

        Returns:
            tuple(True if at least one point was found,
                  Found indexes)
        """
    def GetRefPoint(self) -> Point2D:
        """Get reference point.

        Returns:
            constant the reference point in the world coordinate system.
        """
    def GetRelPoint(self, index: int) -> Point2D:
        """Get point in Local coordinate system, no data.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point constant the point at position index.
        """
    def GetStartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.

        Returns:
            start point in world coordinate system
        """
    def GetStartRelPoint(self) -> Point2D:
        """Get the start point

        Returns:
            start point
        """
    @typing.overload
    def Insert(self, polyPoints: PolyPoints2D, position: int = 18446744073709551615) -> bool:
        """Insert vector of points at specific position.

        If return false then points weren't inserted.

        Args:
            polyPoints: constant the PolyPoints.
            position:   position where points will be inserted.

        Returns:
            bool true if successful.
        """
    @typing.overload
    def Insert(self, point: Point2D, position: int = 18446744073709551615) -> bool:
        """Insert point at specific position. Used world coordinates.

        If return false then points weren't Inserted.

        Args:
            point:    constant the Point.
            position: position where points will be inserted.

        Returns:
            bool true if successful.
        """
    def Insert(self):
        """ Overloaded function. See individual overloads.
        """
    def InsertRel(self, point: Point2D, position: int = 18446744073709551615) -> bool:
        """Insert relative point at specific position. Used local coordinates.

        If return false then points weren't Inserted.

        Args:
            point:    constant the Point.
            position: position where points will be inserted.

        Returns:
            bool true if successful.
        """
    def Remove(self, position: int) -> bool:
        """Remove point from specific position.

        If return false then points weren't removed.

        Args:
            position: position of point which will be removed.

        Returns:
            Point removed: true/false
        """
    def RemoveLastPoint(self) -> bool:
        """Remove the last point

        Returns:
            Point removed: true/false
        """
    def Reserve(self, newCount: int):
        """Reserve container capacity

        Args:
            newCount: Expected size of container [count of points]
        """
    def Resize(self, newSize: int):
        """Specifies a new size for the points vector.

        Args:
            newSize: The new size of the points vector.
        """
    def Reverse(self):
        """Reverse the point order
        """
    def SetEndPoint(self, endpoint: Point2D):
        """Set the end point in world coordinates

        Args:
            endpoint: new end point
        """
    def SetPoint(self, point: Point2D, index: int):
        """Set point at given position in world coordinate system.

        Args:
            point: point in the world coordinate system.
            index: index of point which will be set
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set reference point in world coordinate system.

        Args:
            refPoint: reference point in the world coordinate system.
        """
    def SetRelPoint(self, point: Point2D, index: int):
        """Set point at given position in relative coordinate system.

        Args:
            point: point in the relative coordinate system.
            index: index of point which will be set
        """
    def SetStartPoint(self, startpoint: Point2D):
        """Set the start point in world coordinates

        Args:
            startpoint: new start point
        """
    def ToLineChain(self) -> Point2DList:
        """Get polyline as a chain of lines composed from 2 points.

        Returns:
            vector of lines composed from 2 points (start and end point of a line)
        """
    def __getitem__(self, index: int) -> Point2D:
        """Get point at position from index. Used world coordinates.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point.
        """
    def __iadd__(self, point: Point2D) -> PolyPoints2D:
        """Add point in world coordinates.

        Args:
            point: adding point.

        Returns:
            New point
        """
    def __mul__(self, matrix: Matrix2D) -> PolyPoints2D:
        """2D matrix transformation

        Args:
            matrix: 2D transformation matrix

        Returns:
            Transformed polyline
        """
    def __setitem__(self, arg2: int, value: Point2D):
        """Set point at position from index. Used world coordinates.

        This method is checked and throwing Geometry::Exception when index is out of range.
        Args:
            index: Specified position
            pnt:   Point
        """
    @property
    def EndPoint(self) -> Point2D:
        """Get the end point in world coordinate system.
        """
    @EndPoint.setter
    def EndPoint(self, value: Point2D) -> None:
        """Set the end point in world coordinates
        """
    @property
    def EndRelPoint(self) -> Point2D:
        """Get the end point
        """
    @property
    def Points(self) -> list[Point2D]:
        """Get the point list
        """
    @Points.setter
    def Points(self, value: list[Point2D]) -> None:
        """Set  the point list
        """
    @property
    def RefPoint(self) -> Point2D:
        """Get reference point.
        """
    @RefPoint.setter
    def RefPoint(self, value: Point2D) -> None:
        """Set reference point in world coordinate system.
        """
    @property
    def StartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, value: Point2D) -> None:
        """Set the start point in world coordinates
        """
    @property
    def StartRelPoint(self) -> Point2D:
        """Get the start point
        """

class BSpline2DList():
    """List for BSpline2D objects
    """
    def __contains__(self, value: BSpline2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BSpline2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BSpline2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BSpline2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BSpline2DList:
        """Add a list

        Args:
            eleList: BSpline2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BSpline2D):
        """Constructor with a BSpline2D

        Args:
            ele: BSpline2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BSpline2D

        Args:
            eleList: BSpline2D list
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
    def __setitem__(self, index: (int | slice), value: BSpline2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BSpline2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BSpline2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BSpline2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class PolyPoints3D():
    """The PolyPoints class is the base template class for all objects which store geometry as a vector of points (or another objects), specially for polyline, polygon and spline.
    """
    def Clear(self):
        """Remove all points from vector.
        """
    def Count(self) -> int:
        """Get count of points.

        Returns:
            bool.
        """
    def Empty(self) -> bool:
        """Return true if no points, otherwise false.

        Returns:
            bool.
        """
    def EqualRef(self, polyPoints: PolyPoints3D) -> bool:
        """Test if reference points are equal.

        Args:
            polyPoints: constant the PolyPoints.

        Returns:
            Reference points are equal: true/false
        """
    def GetEndPoint(self) -> Point3D:
        """Get the end point in world coordinate system.

        Returns:
            end point in world coordinate system
        """
    def GetEndRelPoint(self) -> Point3D:
        """Get the end point

        Returns:
            end point
        """
    def GetLastPoint(self) -> Point3D:
        """Get the last point in world coordinate system, data.

        Returns:
            last point in world coordinate system
        """
    def GetPoint(self, index: int) -> Point3D:
        """Get point in world coordinate system, data.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point point in world coordinate system.
        """
    def GetPointIndex(self, point: Point3D) -> tuple[bool, int]:
        """Get index of the given point

        Args:
            point: Searched point

        Returns:
            tuple(True if a point was found,
                  Found index)
        """
    def GetPointIndexes(self, point: Point3D) -> tuple[bool, list[int]]:
        """Get indexes of the given point, in case that several points in the spline
        will have the same coordinates

        Args:
            point: Searched point

        Returns:
            tuple(True if at least one point was found,
                  Found indexes)
        """
    def GetRefPoint(self) -> Point3D:
        """Get reference point.

        Returns:
            constant the reference point in the world coordinate system.
        """
    def GetRelPoint(self, index: int) -> Point3D:
        """Get point in Local coordinate system, no data.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point constant the point at position index.
        """
    def GetStartPoint(self) -> Point3D:
        """Get the start point in world coordinate system.

        Returns:
            start point in world coordinate system
        """
    def GetStartRelPoint(self) -> Point3D:
        """Get the start point

        Returns:
            start point
        """
    @typing.overload
    def Insert(self, polyPoints: PolyPoints3D, position: int = 18446744073709551615) -> bool:
        """Insert vector of points at specific position.

        If return false then points weren't inserted.

        Args:
            polyPoints: constant the PolyPoints.
            position:   position where points will be inserted.

        Returns:
            bool true if successful.
        """
    @typing.overload
    def Insert(self, point: Point3D, position: int = 18446744073709551615) -> bool:
        """Insert point at specific position. Used world coordinates.

        If return false then points weren't Inserted.

        Args:
            point:    constant the Point.
            position: position where points will be inserted.

        Returns:
            bool true if successful.
        """
    def Insert(self):
        """ Overloaded function. See individual overloads.
        """
    def InsertRel(self, point: Point3D, position: int = 18446744073709551615) -> bool:
        """Insert relative point at specific position. Used local coordinates.

        If return false then points weren't Inserted.

        Args:
            point:    constant the Point.
            position: position where points will be inserted.

        Returns:
            bool true if successful.
        """
    def Remove(self, position: int) -> bool:
        """Remove point from specific position.

        If return false then points weren't removed.

        Args:
            position: position of point which will be removed.

        Returns:
            Point removed: true/false
        """
    def RemoveLastPoint(self) -> bool:
        """Remove the last point

        Returns:
            Point removed: true/false
        """
    def Reserve(self, newCount: int):
        """Reserve container capacity

        Args:
            newCount: Expected size of container [count of points]
        """
    def Resize(self, newSize: int):
        """Specifies a new size for the points vector.

        Args:
            newSize: The new size of the points vector.
        """
    def Reverse(self):
        """Reverse the point order
        """
    def SetEndPoint(self, endpoint: Point3D):
        """Set the end point in world coordinates

        Args:
            endpoint: new end point
        """
    def SetPoint(self, point: Point3D, index: int):
        """Set point at given position in world coordinate system.

        Args:
            point: point in the world coordinate system.
            index: index of point which will be set
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set reference point in world coordinate system.

        Args:
            refPoint: reference point in the world coordinate system.
        """
    def SetRelPoint(self, point: Point3D, index: int):
        """Set point at given position in relative coordinate system.

        Args:
            point: point in the relative coordinate system.
            index: index of point which will be set
        """
    def SetStartPoint(self, startpoint: Point3D):
        """Set the start point in world coordinates

        Args:
            startpoint: new start point
        """
    def ToLineChain(self) -> Point3DList:
        """Get polyline as a chain of lines composed from 2 points.

        Returns:
            vector of lines composed from 2 points (start and end point of a line)
        """
    def __getitem__(self, index: int) -> Point3D:
        """Get point at position from index. Used world coordinates.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: point index.

        Returns:
            point.
        """
    def __iadd__(self, point: Point3D) -> PolyPoints3D:
        """Add point in world coordinates.

        Args:
            point: adding point.

        Returns:
            New point
        """
    def __mul__(self, matrix: Matrix2D) -> PolyPoints3D:
        """2D matrix transformation

        Args:
            matrix: 2D transformation matrix

        Returns:
            Transformed polyline
        """
    def __setitem__(self, arg2: int, value: Point3D):
        """Set point at position from index. Used world coordinates.

        This method is checked and throwing Geometry::Exception when index is out of range.
        Args:
            index: Specified position
            pnt:   Point
        """
    @property
    def EndPoint(self) -> Point3D:
        """Get the end point in world coordinate system.
        """
    @EndPoint.setter
    def EndPoint(self, value: Point3D) -> None:
        """Set the end point in world coordinates
        """
    @property
    def EndRelPoint(self) -> Point3D:
        """Get the end point
        """
    @property
    def Points(self) -> list[Point3D]:
        """Get the point list
        """
    @Points.setter
    def Points(self, value: list[Point3D]) -> None:
        """Set  the point list
        """
    @property
    def RefPoint(self) -> Point3D:
        """Get reference point.
        """
    @RefPoint.setter
    def RefPoint(self, value: Point3D) -> None:
        """Set reference point in world coordinate system.
        """
    @property
    def StartPoint(self) -> Point3D:
        """Get the start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, value: Point3D) -> None:
        """Set the start point in world coordinates
        """
    @property
    def StartRelPoint(self) -> Point3D:
        """Get the start point
        """

class BSpline3DList():
    """List for BSpline3D objects
    """
    def __contains__(self, value: BSpline3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BSpline3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BSpline3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BSpline3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BSpline3DList:
        """Add a list

        Args:
            eleList: BSpline3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BSpline3D):
        """Constructor with a BSpline3D

        Args:
            ele: BSpline3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BSpline3D

        Args:
            eleList: BSpline3D list
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
    def __setitem__(self, index: (int | slice), value: BSpline3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BSpline3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BSpline3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BSpline3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class BSpline3DService():
    """Utilities for BSpline
    """
    def AddControlPoint(self, pointIdx: int, coords: Point3D):
        """add control point to B-Spline

        Args:
            pointIdx: index, where new point will be stored
            coords:   coordinates of point
        """
    def AddControlPointOnSegment(self, ray: Vector3D, coords: Point3D) -> tuple[eGeometryErrorCode, int]:
        """add control point to B-Spline's segment given by point

        Args:
            ray:    view vector
            coords: coordinates of point

        Returns:
            segment index
        """
    @staticmethod
    def BSplineToSpline(bspline: BSpline3D) -> Spline3D:
        """convert BSpline3D to Spline

        Args:
            bspline: source BSpline

        Returns:
            resulting Spline
        """
    @staticmethod
    def DiffsToKnots(degree: int, startVal: float) -> NemAll_Python_Utility.VecDoubleList:
        """convert knots differences vector to knot vector (size of vector is increased by 1)

        Args:
            degree:   degree of BSpline owning the knots
            startVal: start of parameter interval (returned by knotsToDiffs())

        Returns:
            vector of differences converted to vector of knots
        """
    def GetControlPointIndex(self, param: float) -> int:
        """calculate control point index from parameter on B-Spline

        Args:
            param: parameter on BSpline
        """
    @staticmethod
    def GetPoints(bSpline: BSpline3D, allInterPoints: bool) -> tuple[Point3DList, Point3DList]:
        """provide interpolated and control points of BSpline

        Args:
            bSpline:        source BSpline
            allInterPoints: if false, the first and the last interpolated points are excluded, if they match with control points

        Returns:
            tuple(list of control points for handles,
                  list of interpolated points for handles)
        """
    def InsertKnot(self, param: float, numInsertionsMultiplicity: int):
        """Insert knot into bspline knot vector (compute new control points, preserve geometry)

        Args:
            param:                     param to insert
            numInsertionsMultiplicity: multiplicity of new knot
        """
    def IsValid(self) -> bool:
        """Check validity of service data

        Returns:
            bool valid = true
        """
    @staticmethod
    def KnotsToDiffs(degree: int, periodic: bool) -> tuple[float, NemAll_Python_Utility.VecDoubleList]:
        """convert knots vector to knot differences vector (size of vector is decreased by 1)

        Args:
            degree:   degree of BSpline owning the knots
            periodic: true if bspline is periodic (or closed for degree == 1)

        Returns:
            tuple(BSpline parameter interval start,
                  vector of knots converted to vector of differences)
        """
    @staticmethod
    def MergeKnots(newknots: NemAll_Python_Utility.VecDoubleList,
                   newknotMultiplicities: NemAll_Python_Utility.VecSizeTList) -> tuple[NemAll_Python_Utility.VecDoubleList, NemAll_Python_Utility.VecSizeTList]:
        """merge knot values with their multiplicities into input vector

        Args:
            newknots:              knot values to merge
            newknotMultiplicities: knot multiplicities to merge

        Returns:
            tuple(knot values,
                  knot multiplicities)
        """
    def MoveStartPeriodic(self, startParam: float):
        """Move start point in periodic BSpline

        Args:
            startParam: start value for knot interval
        """
    def PointModification(self, pointsIdx: NemAll_Python_Utility.VecSizeTList, moveVector: Vector3D, isInterpolated: bool,
                          hSet: HealingSettings):
        """move interpolated or control point of B-Spline

        Args:
            pointsIdx:      point indexes
            moveVector:     move vector
            isInterpolated: true if wanted to handle interpolated points
            hSet:           healing settings
        """
    def RefineKnots(self, knotvalues: NemAll_Python_Utility.VecDoubleList, knotMultiplicities: NemAll_Python_Utility.VecSizeTList):
        """Refine knots (insert knots if necessary)

        Args:
            knotvalues:         knot values to refine
            knotMultiplicities: knot multiplicities
        """
    def RemoveControlPoint(self, pointIdx: int):
        """remove control point from B-Spline

        Args:
            pointIdx: point index to remove
        """
    @staticmethod
    def ScaleKnots(newStartParam: float, newEndParam: float) -> NemAll_Python_Utility.VecDoubleList:
        """Scale knot vector to new interval

        Args:
            newStartParam: new interval start
            newEndParam:   new interval end

        Returns:
            knot vector
        """
    def SetControlPoint(self, pointIdx: int, newCoords: Point3D):
        """set coordinates of control point of B-Spline

        Args:
            pointIdx:  point index
            newCoords: new coordinates of point
        """
    def SetDegree(self, degree: int):
        """set degree of B-Spline

        Args:
            degree: new degree for B-Spline
        """
    def SetInterpolatedPoint(self, pointIdx: int, newCoords: Point3D):
        """set coordinates of interpolated point of B-Spline

        Args:
            pointIdx:  point index
            newCoords: new coordinates of point
        """
    def SetPeriodic(self, periodic: bool):
        """set/unset periodic property of B-Spline

        Args:
            periodic: it true, B-Spline will be periodic, otherwise B-Spline will be open
        """
    @staticmethod
    def SplineToBSpline(spline: Spline3D) -> BSpline3D:
        """convert Spline3D to BSpline

        Args:
            spline: source Spline

        Returns:
            resulting BSpline
        """
    @typing.overload
    def __init__(self, bSpline: BSpline3D):
        """Constructor

        Args:
            bSpline: B-Spline
        """
    @typing.overload
    def __init__(self, element: BSpline3DService):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class BSplineSurface3D():
    """class for 3D (non uniform, rational) B-spline surface geometry
    """
    def Clear(self):
        """Clear data, getting invalid state
        """
    def Get(self) -> tuple[Point3DList, NemAll_Python_Utility.VecDoubleList, NemAll_Python_Utility.VecDoubleList,
            NemAll_Python_Utility.VecDoubleList, int, int, bool, bool, bool, bool]:
        """Get all surface members

        Returns:
            tuple(all control points,
                  all control points weights,
                  knots in u direction,
                  knots in v direction,
                  degree in u direction,
                  degree in v direction,
                  periodic in u direction,
                  periodic in v direction,
                  closed in u direction,
                  closed in v direction)
        """
    def GetCenterPoint(self) -> Point3D:
        """Get center point

        Returns:
            center point
        """
    def GetNormalVector(self, uv: Point2D) -> tuple[eGeometryErrorCode, Vector3D]:
        """Evaluate normal vector for given parameters

        Args:
            uv: uv paramaters

        Returns:
            tuple(error code,
                  result vector)
        """
    def GetPoints(self) -> Point3DList:
        """Get control points

        Returns:
            all control points
        """
    def GetUDegree(self) -> int:
        """Get surface u-degree

        Returns:
            surface degree
        """
    def GetUKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get u-knot vector

        Returns:
            knot vector const reference
        """
    def GetUPointsCount(self) -> int:
        """Get control points count in u-direction

        Returns:
            size_t control points count
        """
    def GetVDegree(self) -> int:
        """Get surface v-degree

        Returns:
            surface degree
        """
    def GetVKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get v-knot vector

        Returns:
            knot vector const reference
        """
    def GetVPointsCount(self) -> int:
        """Get control points count in v-direction

        Returns:
            size_t control points count
        """
    def GetWeights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights

        Returns:
            weights vector const reference
        """
    def IsPlanar(self) -> bool:
        """Check if surface is planar

        Returns:
            bool true = yes
        """
    def IsRational(self) -> bool:
        """Check if the surface is rational

        Returns:
            bool true = rational
        """
    def IsUClosed(self) -> bool:
        """Check if the surface is closed in U direction

        Returns:
            bool true = closed
        """
    def IsUPeriodic(self) -> bool:
        """Check if the surface is periodic in U direction

        Returns:
            bool true = periodic
        """
    def IsVClosed(self) -> bool:
        """Check if the surface is closed in V direction

        Returns:
            bool true = closed
        """
    def IsVPeriodic(self) -> bool:
        """Check if the surface is periodic in V direction

        Returns:
            bool true = periodic
        """
    def IsValid(self) -> bool:
        """Check surface validity

        Returns:
            bool valid = true
        """
    def Set(self, points: Point3DList, weights: NemAll_Python_Utility.VecDoubleList, uknots: NemAll_Python_Utility.VecDoubleList,
            vknots: NemAll_Python_Utility.VecDoubleList, udegree: int, vdegree: int, isUPeriodic: bool, isVPeriodic: bool, isUClosed: bool, isVClosed: bool):
        """Set all surface members

        Args:
            points:      all control points
            weights:     all control points weights
            uknots:      knots in u direction
            vknots:      knots in v direction
            udegree:     degree in u direction
            vdegree:     degree in v direction
            isUPeriodic: periodic in u direction
            isVPeriodic: periodic in v direction
            isUClosed:   closed in u direction
            isVClosed:   closed in v direction
        """
    def SetUDegree(self, degree: int):
        """Set surface v-degree

        Args:
            degree: desired degree
        """
    def SetUKnots(self, knots: NemAll_Python_Utility.VecDoubleList):
        """Set u-knot vector

        Args:
            knots: knot vector to set
        """
    def SetVDegree(self, degree: int):
        """Set surface v-degree

        Args:
            degree: desired degree
        """
    def SetVKnots(self, knots: NemAll_Python_Utility.VecDoubleList):
        """Set v-knot vector

        Args:
            knots: knot vector to set
        """
    def SetWeights(self, weights: NemAll_Python_Utility.VecDoubleList):
        """Set weights for control points

        Args:
            weights: weights vector to set
        """
    def __eq__(self, bsplinesrfc: BSplineSurface3D) -> object:
        """Comparison of BSplineSurface3D without tolerance.

        Be careful, this method work without tolerance!

        Args:
            bsplinesrfc:Compared BSplineSurface3D.

        Returns:
            True when BSplineSurface3D are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, points: Point3DList, weights: NemAll_Python_Utility.VecDoubleList, uknots: NemAll_Python_Utility.VecDoubleList,
                 vknots: NemAll_Python_Utility.VecDoubleList, udegree: int, vdegree: int, isUPeriodic: bool, isVPeriodic: bool, isUClosed: bool, isVClosed: bool):
        """Constructor

        Args:
            points:      all control points
            weights:     all control points weights
            uknots:      knots in u direction
            vknots:      knots in v direction
            udegree:     degree in u direction
            vdegree:     degree in v direction
            isUPeriodic: periodic in u direction
            isVPeriodic: periodic in v direction
            isUClosed:   closed in u direction
            isVClosed:   closed in v direction
        """
    @typing.overload
    def __init__(self, surface: BSplineSurface3D):
        """Copy constructor.

        Args:
            surface: Surface which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def CenterPoint(self) -> Point3D:
        """Get center point
        """
    @property
    def Planar(self) -> bool:
        """Check if surface is planar
        """
    @Planar.setter
    def Planar(self, value: bool) -> None:
        """Check if surface is planar
        """
    @property
    def Points(self) -> void:
        """Get control points
        """
    @property
    def Rational(self) -> bool:
        """Check if the surface is rational
        """
    @Rational.setter
    def Rational(self, value: bool) -> None:
        """Check if the surface is rational
        """
    @property
    def UClosed(self) -> bool:
        """Check if the surface is closed in U direction
        """
    @UClosed.setter
    def UClosed(self, value: bool) -> None:
        """Check if the surface is closed in U direction
        """
    @property
    def UDegree(self) -> int:
        """Get surface u-degree
        """
    @UDegree.setter
    def UDegree(self, degree: int) -> None:
        """Set surface v-degree

        Args:
            degree: desired degree
        """
    @property
    def UKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get u-knot vector
        """
    @UKnots.setter
    def UKnots(self, knots: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set u-knot vector

        Args:
            knots: knot vector to set
        """
    @property
    def UPeriodic(self) -> bool:
        """Check if the surface is periodic in U direction
        """
    @UPeriodic.setter
    def UPeriodic(self, value: bool) -> None:
        """Check if the surface is periodic in U direction
        """
    @property
    def UPointsCount(self) -> int:
        """Get control points count in u-direction
        """
    @property
    def VClosed(self) -> bool:
        """Check if the surface is closed in V direction
        """
    @VClosed.setter
    def VClosed(self, value: bool) -> None:
        """Check if the surface is closed in V direction
        """
    @property
    def VDegree(self) -> int:
        """Get surface v-degree
        """
    @VDegree.setter
    def VDegree(self, degree: int) -> None:
        """Set surface v-degree

        Args:
            degree: desired degree
        """
    @property
    def VKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get v-knot vector
        """
    @VKnots.setter
    def VKnots(self, knots: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set v-knot vector

        Args:
            knots: knot vector to set
        """
    @property
    def VPeriodic(self) -> bool:
        """Check if the surface is periodic in V direction
        """
    @VPeriodic.setter
    def VPeriodic(self, value: bool) -> None:
        """Check if the surface is periodic in V direction
        """
    @property
    def VPointsCount(self) -> int:
        """Get control points count in v-direction
        """
    @property
    def Valid(self) -> bool:
        """Check surface validity
        """
    @Valid.setter
    def Valid(self, value: bool) -> None:
        """Check surface validity
        """
    @property
    def Weights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights
        """
    @Weights.setter
    def Weights(self, weights: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set weights for control points

        Args:
            weights: weights vector to set
        """

class BSplineSurface3DList():
    """List for BSplineSurface3D objects
    """
    def __contains__(self, value: BSplineSurface3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BSplineSurface3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BSplineSurface3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BSplineSurface3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BSplineSurface3DList:
        """Add a list

        Args:
            eleList: BSplineSurface3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BSplineSurface3D):
        """Constructor with a BSplineSurface3D

        Args:
            ele: BSplineSurface3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BSplineSurface3D

        Args:
            eleList: BSplineSurface3D list
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
    def __setitem__(self, index: (int | slice), value: BSplineSurface3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BSplineSurface3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BSplineSurface3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BSplineSurface3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class BoundingBox2D():
    """Representation class for 2D bounding box.

    Bounding box work correct only if m_Min <= m_Max. It means that X coordinate of m_Min is less then or
    equal to X coordinate of m_Max(m_Min.X() <= m_Max.X()) and Y coordinate of m_Min is less than or equal to Y coordinate
    of m_Max(m_Min.Y() <= m_Max.Y()).
    """
    @typing.overload
    def Deflate(self, x: float, y: float):
        """Deflate in x and y axis

        Args:
            x: deflate in X axis
            y: deflate in Y axis
        """
    @typing.overload
    def Deflate(self, size: float):
        """Deflate in x,y axis concurrently.

        Args:
            size: deflate in x and y axis concurrently.
        """
    def Deflate(self):
        """ Overloaded function. See individual overloads.
        """
    def Get(self) -> tuple[Point2D, Point2D, Angle]:
        """Get minimum point, maximum point and angle

        Returns:
            tuple(minimum point in local coordinate system,
                  maximum point in local coordinate system,
                  direction of X axis of new coordinate system)
        """
    def GetAngle(self) -> Angle:
        """Get direction of X axis of new coordinate system

        Returns:
            angle direction of X axis of new coordinate system
        """
    def GetBoxPoint(self, _BoxPointLocation: eBoxPoint) -> Point2D:
        """Get the box point

        Args:
            _BoxPointLocation: Box point location

        Returns:
            Box point
        """
    def GetCenter(self) -> Point2D:
        """Get box center point in local coordinate system

        Returns:
            center point in local coordinates system
        """
    def GetCenterPoint(self) -> Point2D:
        """Get world point at center of box

        Returns:
            Point2D
        """
    def GetHeight(self) -> float:
        """Get height of box in local system

        Returns:
            double
        """
    def GetMax(self) -> Point2D:
        """Get maximum point in local coordinate system

        Returns:
            maximum point in local coordinate system
        """
    def GetMaxPoint(self) -> Point2D:
        """Get world point at maximum of box

        Returns:
            Point2D
        """
    def GetMin(self) -> Point2D:
        """Get minimum point in local coordinate system

        Returns:
            minimum point
        """
    def GetMinPoint(self) -> Point2D:
        """Get world point at maximum of box

        Returns:
            Point2D
        """
    def GetWidth(self) -> float:
        """Get width of box in local system

        Returns:
            double
        """
    @typing.overload
    def Inflate(self, x: float, y: float):
        """Inflate in x and y axis

        Args:
            x: inflate in X axis
            y: inflate in Y axis
        """
    @typing.overload
    def Inflate(self, size: float):
        """Inflate in x,y axis concurrently.

        Args:
            size: inflate in x and y axis concurrently.
        """
    def Inflate(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def IsContaining(self, point: Point2D) -> bool:
        """Is point inside this box

        Args:
            point: point in world coordinate system

        Returns:
            true, if is inside, otherwise false
        """
    @typing.overload
    def IsContaining(self, box: BoundingBox2D) -> bool:
        """Is box inside this box

        Args:
            box: bounding box

        Returns:
            true, if is inside, otherwise false
        """
    @typing.overload
    def IsContaining(self, minmax: MinMax2D) -> bool:
        """Is minmax box inside this box

        Args:
            minmax: minmax box

        Returns:
            true, if is inside, otherwise false
        """
    def IsContaining(self):
        """ Overloaded function. See individual overloads.
        """
    def IsValid(self) -> bool:
        """Test if box is valid

        Returns:
            true, if box valid, otherwise false
        """
    @typing.overload
    def Overlaps(self, box: BoundingBox2D) -> bool:
        """Does box overlap this box

        Args:
            box: bounding box

        Returns:
            true, if boxes overlap, otherwise false
        """
    @typing.overload
    def Overlaps(self, minmax: MinMax2D) -> bool:
        """Does minmax box overlap this box

        Args:
            minmax: MinMax2D box

        Returns:
            true, if boxes overlap, otherwise false
        """
    def Overlaps(self):
        """ Overloaded function. See individual overloads.
        """
    def Reset(self, angle: Angle):
        """Reset bounding box and set initial angle

        When bounding box is reseted, then
         min point is initialized to [DBL_MAX,DBL_MAX],
         max point to [-DBL_MAX,-DBL_MAX],

        This method is using when previous initialized bounding box start accept a new point values.

        Args:
            angle: Initial angle
        """
    def Set(self, min: Point2D, max: Point2D, angle: Angle):
        """Set minimum point, maximum point and angle

        Args:
            min:   minimum point in local coordinate system
            max:   maximum point in local coordinate system
            angle: angle between world X and local X coordinate system
        """
    def SetAngle(self, angle: Angle):
        """Set direction of X axis of new coordinate system

        Args:
            angle: direction of X axis of new coordinate system
        """
    def SetHeight(self, height: float):
        """Set height of box in local system. Computed from Min point

        Args:
            height: Height
        """
    def SetMax(self, max: Point2D):
        """Set maximum point in local coordinate system

        Args:
            max: maximum point
        """
    def SetMin(self, min: Point2D):
        """Set minimum point

        Args:
            min: minimum point in local coordinate system
        """
    def SetWidth(self, width: float):
        """Set width of box in local system. Computed from Min point

        Args:
            width:  Width
        """
    @typing.overload
    def __add__(self, boundingBox: BoundingBox2D) -> BoundingBox2D:
        """Expand BoundingBox2D box.

        Expands the BoundingBox2D box by the box given in parameter minmax

        Args:
            boundingBox: BoundingBox2D to be added

        Returns:
            BoundingBox2D box.
        """
    @typing.overload
    def __add__(self, minMax: MinMax2D) -> BoundingBox2D:
        """Expand BoundingBox2D box by given MinMax2D.

        Expands the BoundingBox2D box by the minmax box given in parameter minmax

        Args:
            minMax: MinMax2D to be added

        Returns:
            BoundingBox2D box.
        """
    def __add__(self, dummy: typing.Any):
        """ Overloaded function. See individual overloads.

        Args:
            dummy:  dummy parameter

        Returns:
            dummy
        """
    def __eq__(self, bounding_box: BoundingBox2D) -> bool:
        """Comparison of bounding boxes.

        Be careful, this method work without tolerance!

        Args:
            bounding_box: bounding box to be compared.

        Returns:
            True when bounding boxes are equal, otherwise false.
        """
    def __getitem__(self, index: int) -> Point2D:
        """Get the corners of bounding box.

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: corner index (0-left bottom, 1-right bottom, 2-right top, 3-left top)

        Returns:
            corner as Point2D in world coordinate system.
        """
    @typing.overload
    def __iadd__(self, boundingBox: BoundingBox2D) -> BoundingBox2D:
        """Expand BoundingBox2D box.

        Expands the BoundingBox2D box by the box given in parameter minmax

        Args:
            boundingBox: BoundingBox2D to be added

        Returns:
            BoundingBox2D box.
        """
    @typing.overload
    def __iadd__(self, minmax: MinMax2D) -> BoundingBox2D:
        """Expand BoundingBox2D box by given MinMax2D.

        Expands the BoundingBox2D box by the minmax box given in parameter minmax

        Args:
            minmax: MinMax2D to be added

        Returns:
            BoundingBox2D.
        """
    @typing.overload
    def __iadd__(self, point: Point2D) -> BoundingBox2D:
        """Expand BoundingBox2D box.

        Expands the BoundingBox2D box by the Point2D given in parameter point

        Args:
            point: Point2D to be added in world coordinate system

        Returns:
            bounding box.
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, angle: Angle):
        """Default constructor.

        min point is initialized to [DBL_MAX,DBL_MAX],
        max point to [-DBL_MAX,-DBL_MAX],

        Args:
            angle: Angle of new initialized bounding box.
        """
    @typing.overload
    def __init__(self, min: Point2D, max: Point2D, angle: Angle):
        """Set constructor

        Initialize bounding box with given MIN, MAX points and slew of local coordinate system.

        Args:
            min:   minimum point in local coordinate system
            max:   maximum point in local coordinate system
            angle: direction of X axis of local coordinate system
        """
    @typing.overload
    def __init__(self, boundingBox2D: BoundingBox2D):
        """Copy constructor.

        Args:
            boundingBox2D: BoundingBox2D to be copied
        """
    @typing.overload
    def __init__(self, minMax2D: MinMax2D):
        """Copy constructor.

        Args:
            minMax2D: MinMax2D to be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Angle(self) -> Angle:
        """Get direction of X axis of new coordinate system
        """
    @Angle.setter
    def Angle(self, angle: Angle) -> None:
        """Set direction of X axis of new coordinate system

        Args:
            angle: direction of X axis of new coordinate system
        """
    @property
    def Height(self) -> float:
        """Get height of box in local system
        """
    @Height.setter
    def Height(self, height: float) -> None:
        """Set height of box in local system. Computed from Min point

        Args:
            height: Height
        """
    @property
    def Max(self) -> Point2D:
        """Get maximum point in local coordinate system
        """
    @Max.setter
    def Max(self, max: Point2D) -> None:
        """Set maximum point in local coordinate system

        Args:
            max: maximum point
        """
    @property
    def Min(self) -> Point2D:
        """Get minimum point in local coordinate system
        """
    @Min.setter
    def Min(self, min: Point2D) -> None:
        """Set minimum point

        Args:
            min: minimum point in local coordinate system
        """
    @property
    def Width(self) -> float:
        """Get width of box in local system
        """
    @Width.setter
    def Width(self, width: float) -> None:
        """Set width of box in local system. Computed from Min point

        Args:
            width: Width
        """

class BoundingBox2DList():
    """List for BoundingBox2D objects
    """
    def __contains__(self, value: BoundingBox2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: BoundingBox2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: BoundingBox2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> BoundingBox2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> BoundingBox2DList:
        """Add a list

        Args:
            eleList: BoundingBox2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: BoundingBox2D):
        """Constructor with a BoundingBox2D

        Args:
            ele: BoundingBox2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of BoundingBox2D

        Args:
            eleList: BoundingBox2D list
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
    def __setitem__(self, index: (int | slice), value: BoundingBox2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: BoundingBox2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: BoundingBox2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: BoundingBox2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class CenterCalculus():
    """Class to calculate the center of an object
    """
    @staticmethod
    @typing.overload
    def Calculate(line: Line2D) -> tuple:
        """Calculates the center of a 2D line

        Args:
            line:  Line2D on which to calculate the center

        Returns:
            True when calculation was successful. False otherwise
            Center of the line
        """
    @staticmethod
    @typing.overload
    def Calculate(line: Line3D) -> tuple:
        """Calculates the center of a 3D line

        Args:
            line:  Line3D on which to calculate the center

        Returns:
            True when calculation was successful. False otherwise
            Center of the line
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline: Polyline2D, edge: int) -> tuple:
        """Calculates the center of a 2D polyline

        Args:
            polyline:   Polyline on which to calculate the center.
            edge:       Index of the segment to calculate the center on.
                        Set to 0 to calculate the center of the entire polyline.

        Returns:
            True when calculation was successful. False otherwise
            Center of the polyline or its segment
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline: Polyline3D, edge: int) -> tuple:
        """Calculates the center of a 3D polyline

        Args:
            polyline:   Polyline on which to calculate the center.
            edge:       Index of the segment to calculate the center on.
                        Set to 0 to calculate the center of the entire polyline.

        Returns:
            True when calculation was successful. False otherwise
            Center of the polyline or its segment
        """
    @staticmethod
    @typing.overload
    def Calculate(polygon: Polygon2D, bPlaneCenter: bool, edge: int) -> tuple:
        """Calculates the center of a 2D polygon.

        Args:
            polygon:        Polygon on which to calculate the center
            bPlaneCenter:   Whether to calculate the center of the area bounded by the polygon (True)
                            or the center of the outline polyline (False)
            edge:           When bPlaneCenter is set to False, this is the index of the segment of
                            the outline polyline to calculate the center on. Set to 0 to calculate
                            the center of the entire outline polyline.

        Returns:
            True when calculation was successful. False otherwise.
            Center of the polygon or its outline
        """
    @staticmethod
    @typing.overload
    def Calculate(polygon: Polygon3D, bPlaneCenter: bool, edge: int) -> tuple:
        """Calculates the center of a 3D polygon.

        Args:
            polygon:        Polygon on which to calculate the center
            bPlaneCenter:   Whether to calculate the center of the area bounded by the polygon (True)
                            or the center of the outline polyline (False)
            edge:           When bPlaneCenter is set to False, this is the index of the segment of
                            the outline polyline to calculate the center on. Set to 0 to calculate
                            the center of the entire outline polyline.

        Returns:
            True when calculation was successful. False otherwise.
            Center of the polygon or its outline
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc2D, center: bool) -> tuple:
        """Calculates the center of a 2D arc.

        Args:
            arc:      arc on which to calculate the center
            center:   Whether to calculate the arc's **midpoint**, that divides the arc into two halves (True)
                      or the arc's **center** (False)

        Returns:
            True when calculation was successful. False otherwise.
            Center or midpoint of the arc
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc3D, center: bool) -> tuple:
        """Calculates the center of a 3D arc.

        Args:
            arc:      arc on which to calculate the center
            center:   Whether to calculate the arc's **midpoint**, that divides the arc into two halves (True)
                      or the arc's **center** (False)

        Returns:
            True when calculation was successful. False otherwise.
            Center or midpoint of the arc
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: Spline2D, eps: float) -> tuple:
        """Calculates the center of a 2D spline.

        Args:
            spline:  Spline on which to calculate the center
            eps:     Precision for calculation

        Returns:
            True when calculation was successful. False otherwise.
            Center of the spline
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: Spline3D, eps: float) -> tuple:
        """Calculates the center of a 3D spline.

        Args:
            spline:  Spline on which to calculate the center
            eps:     Precision for calculation

        Returns:
            True when calculation was successful. False otherwise.
            Center of the spline
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: BSpline3D, eps: float, bAreaCenter: bool) -> tuple:
        """Calculates the center of a 3D base spline.

        Args:
            spline:       B-spline on which to calculate the center
            eps:          Precision for calculation
            bAreaCenter:  In case of a **closed** b-spline: whether to calculate the center of the area
                          bounded by the B-spline (True) or the center of the b-spline curve (False)

        Returns:
            True when calculation was successful. False otherwise.
            Center of the b-spline
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: BSpline2D, eps: float) -> tuple:
        """Calculates the center of a 2D base spline.

        Args:
            spline:       B-spline on which to calculate the center
            eps:          Precision for calculation

        Returns:
            True when calculation was successful. False otherwise.
            Center of the b-spline
        """
    @staticmethod
    @typing.overload
    def Calculate(clothoid: Clothoid2D, eps: float) -> tuple:
        """Calculates the center of a 2D clothoid.

        Args:
            clothoid:     clothoid on which to calculate the center
            eps:          Precision for calculation

        Returns:
            True when calculation was successful. False otherwise.
            Center of the clothoid
        """
    @staticmethod
    @typing.overload
    def Calculate(path: Path2D, eps: float, bAreaCenter: bool) -> tuple:
        """Calculates the center of a 2D path.

        Args:
            path:         Path on which to calculate the center
            eps:          Precision for calculation
            bAreaCenter:  In case of a **closed** path: whether to calculate the center of the area
                          bounded by the path (True) or the center of the path itself (False)

        Returns:
            True when calculation was successful. False otherwise.
            Center of the path
        """
    @staticmethod
    @typing.overload
    def Calculate(path: Path3D, eps: float, bAreaCenter: bool) -> tuple:
        """Calculates the center of a 3D path.

        Args:
            path:         Path on which to calculate the center
            eps:          Precision for calculation
            bAreaCenter:  In case of a **closed** path: whether to calculate the center of the area
                          bounded by the path (True) or the center of the path itself (False)

        Returns:
            True when calculation was successful. False otherwise.
            Center of the path
        """
    @staticmethod
    @typing.overload
    def Calculate(geoObject: object, eps: float, bArcCenter: bool, edge: int) -> tuple:
        """Calculates the center of a curve.

        Args:
            geoObject:  object on which to calculate the center
            eps:        Precision for calculation
            bArcCenter: Whether to calculate the arc's **midpoint**, that divides the arc into two halves (True)
                        or the arc's **center** (False)
            edge:       For polyline and polygon: index of the segment to calculate the center on.
                        Set to 0 to calculate the center of the entire polyline/polygon.

        Returns:
            True when calculation was successful. False otherwise.
            Center of the path
        """
    def Calculate(self):
        """Calculates the center of a curve.

        Args:
            geoObject:  object on which to calculate the center
            eps:        Precision for calculation
            bArcCenter: Whether to calculate the arc's **midpoint**, that divides the arc into two halves (True)
                        or the arc's **center** (False)
            edge:       For polyline and polygon: index of the segment to calculate the center on.
                        Set to 0 to calculate the center of the entire polyline/polygon.

        Returns:
            True when calculation was successful. False otherwise.
            Center of the path
        """

class ChamferCalculus():
    """Class for chamfer calculation between two objects
    """
    @staticmethod
    @typing.overload
    def Calculate(polyhedron: Polyhedron3D, chamferWidth: float) -> tuple:
        """Calculate chamfer on all edges of given Polyhedron3D

        Args:
            polyhedron:   polyhedron to chamfer
            chamferWidth: chamfer width

        Returns:
            error code,
            Resulting polyhedron
        """
    @staticmethod
    @typing.overload
    def Calculate(polyhedron: Polyhedron3D, edges: NemAll_Python_Utility.VecSizeTList, chamferWidth: float, propagation: bool) -> tuple:
        """Calculate chamfer on selected edges of given Polyhedron3D

        Args:
            polyhedron:   polyhedron to chamfer
            edges:        edges to chamfer
            chamferWidth: chamfer width
            propagation:  flag for propagation of neighboring edges

        Returns:
            error code,
            Resulting polyhedron
        """
    @staticmethod
    @typing.overload
    def Calculate(brep: BRep3D, chamferWidth: float) -> tuple:
        """Calculate chamfer on all edges of given BRep3D

        Args:
            brep:         BRep to chamfer
            chamferWidth: chamfer width

        Returns:
            error code,
            Resulting BRep
        """
    @staticmethod
    @typing.overload
    def Calculate(brep: BRep3D, edges: NemAll_Python_Utility.VecSizeTList, chamferWidth: float, propagation: bool) -> tuple:
        """Calculate chamfer on selected edges of given BRep3D

        Args:
            brep:         BRep to chamfer
            edges:        edges to chamfer
            chamferWidth: chamfer width
            propagation:  flag for propagation of neighboring edges

        Returns:
            error code,
            Resulting BRep
        """
    def Calculate(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def CalculateApplicableChamfers(line1: Line2D, line2: Line2D, intersectionPoint: Point2D, chamferWidth: float) -> Line2DList:
        """Calculates four applicable chamfer lines

        Args:
            line1:             Geometry of first chamfered line
            line2:             Geometry of second chamfered line
            intersectionPoint: Intersection point of 2 chamfered lines
            chamferWidth:      Chamfer width

        Returns:
            Calculated 4 applicable chamfer lines
        """
    @staticmethod
    @typing.overload
    def CalculateApplicableChamfers(igeo1: object, igeo2: object, plane3D: Plane3D, intersectionPoint: Point3D,
                                    chamferWidth: float) -> Line3DList:
        """Calculates four applicable chamfer lines

        Args:
            igeo1:             Geometry of first object
            igeo2:             Geometry of second object
            plane3D:           3D plane in which objects lie
            intersectionPoint: Intersection point of 2 chamfered objects
            chamferWidth:      Chamfer width

        Returns:
            Calculated 4 applicable chamfer lines
        """
    @staticmethod
    @typing.overload
    def CalculateApplicableChamfers(line1: Line3D, line2: Line3D, plane3D: Plane3D, intersectionPoint: Point3D,
                                    chamferWidth: float) -> Line3DList:
        """Calculates applicable chamfer lines between two 3D lines

        Args:
            line1:             Geometry of the first line
            line2:             Geometry of the second line
            plane3D:           3D plane in which line lies
            intersectionPoint: Intersection point of 2 chamfered lines
            chamferWidth:      Chamfer width

        Returns:
            Calculated 4 applicable chamfer lines
        """
    @staticmethod
    @typing.overload
    def CalculateApplicableChamfers(line: Line3D, arc: Arc3D, chamferArc: Arc3D, bFirstElementIsLine: bool) -> Line3DList:
        """Calculates applicable chamfer lines between 3D line and 3D arc

        Args:
            line:                Geometry of 3D line
            arc:                 Geometry of 3D arc
            chamferArc:          Geometry of chamfer arc
            bFirstElementIsLine: Flag for order of element's intersection calculation

        Returns:
            Calculated 4 applicable chamfer lines
        """
    @staticmethod
    @typing.overload
    def CalculateApplicableChamfers(arc1: Arc3D, arc2: Arc3D, chamferArc: Arc3D) -> Line3DList:
        """Calculates applicable chamfer lines between two 3D arcs

        Args:
            arc1:       Geometry of the first arc
            arc2:       Geometry of the second arc
            chamferArc: Geometry of chamfer arc

        Returns:
            Calculated 4 applicable chamfer lines
        """
    def CalculateApplicableChamfers(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def CalculateChamferInsideOnePolyline(originalChamferLine: Line3D, originalPolyLine: Polyline3D, polySegment1: int,
                                          polySegment2: int) -> Polyline3D:
        """Calculate chamfer inside one polyline - 2 different segments of a polyline are to be chamfered

        Args:
            originalChamferLine: Geometry of chamfer line
            originalPolyLine:    Geometry of chamfered polyline
            polySegment1:        First segment index of polyline
            polySegment2:        Second segment index of polyline

        Returns:
               Calculated chamfered polyline
        """
    @staticmethod
    @typing.overload
    def CalculateChamferLine(line1: Line2D, line2: Line2D, inputPoint: Point2D) -> Line2D:
        """Calculates chamfer line

        Args:
            line1:      Geometry of first chamfered line
            line2:      Geometry of second chamfered line
            inputPoint: Point of click (through which the chamfer should run)

        Returns:
            Calculated chamfer line
        """
    @staticmethod
    @typing.overload
    def CalculateChamferLine(igeo1: object, igeo2: object, plane3D: Plane3D, intersectionPoint: Point3D, inputPoint: Point3D) -> Line3D:
        """Calculates chamfer line

        Args:
            igeo1:             Geometry of first object
            igeo2:             Geometry of second object
            plane3D:           3D plane of the objects
            intersectionPoint: Intersection point of objects for chamfering
            inputPoint:        Point of click (through which the chamfer should run)

        Returns:
               Calculated chamfer line
        """
    @staticmethod
    @typing.overload
    def CalculateChamferLine(line1: Line3D, line2: Line3D, plane3D: Plane3D, intersectionPoint: Point3D, inputPoint: Point3D) -> Line3D:
        """Calculates chamfer line between two 3D lines

        Args:
            line1:             Geometry of first 3D line
            line2:             Geometry of second 3D line
            plane3D:           3D plane of the objects
            intersectionPoint: Intersection point of objects for chamfering
            inputPoint:        Point of click (through which the chamfer should run)

        Returns:
               Calculated chamfer line
        """
    @staticmethod
    @typing.overload
    def CalculateChamferLine(line: Line3D, arc: Arc3D, plane3D: Plane3D, intersectionPoint: Point3D, inputPoint: Point3D,
                             bFirstElementIsLine: bool) -> Line3D:
        """Calculates chamfer line between 3D line and 3D arc

        Args:
            line:                Geometry of 3D line
            arc:                 Geometry of 3D arc
            plane3D:             3D plane of the objects
            intersectionPoint:   Intersection point of objects for chamfering
            inputPoint:          Point of click (through which the chamfer should run)
            bFirstElementIsLine: Flag for order of element's intersection calculation

        Returns:
               Calculated chamfer line
        """
    @staticmethod
    @typing.overload
    def CalculateChamferLine(arc1: Arc3D, arc2: Arc3D, plane3D: Plane3D, intersectionPoint: Point3D, inputPoint: Point3D) -> Line3D:
        """Calculates chamfer line between two 3D arcs

        Args:
            arc1:              Geometry of the first 3D arc
            arc2:              Geometry of the second 3D arc
            plane3D:           3D plane of the objects
            intersectionPoint: Intersection point of objects for chamfering
            inputPoint:        Point of click (through which the chamfer should run)

        Returns:
               Calculated chamfer line
        """
    def CalculateChamferLine(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def CalculateChamferedLine(originalLine: Line2D, intersectionPoint: Point2D, chamferPoint: Point2D) -> Line2D:
        """Calculates chamfered line

        Args:
            originalLine:      Line which is being chamfered
            intersectionPoint: Intersection point of 2 chamfered lines
            chamferPoint:      Intersection point of chamfer line and (original) chamfered line

        Returns:
            Calculated chamfered line
        """
    @staticmethod
    @typing.overload
    def CalculateChamferedLine(originalLine: Line3D, plane3D: Plane3D, intersectionPoint: Point3D, chamferPoint: Point3D) -> Line3D:
        """Calculates chamfered line

        Args:
            originalLine:      Line which is being chamfered
            plane3D:           3D plane in which line lies
            intersectionPoint: Intersection point of 2 chamfered lines
            chamferPoint:      Intersection point of chamfer line and (original) chamfered line

        Returns:
               Calculated chamfered line
        """
    def CalculateChamferedLine(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def CalculateHalvingAngle(line1: Line2D, line2: Line2D, intersectionPoint: Point2D) -> Angle:
        """Calculates halving angle of 2 given lines in the global coordinate system

        Args:
            line1:             Geometry of first line
            line2:             Geometry of second line
            intersectionPoint: Intersection point of the 2 lines

        Returns:
            Halving angle
        """
    @staticmethod
    @typing.overload
    def SwapLinePoints(line: Line2D, point: Point2D) -> tuple:
        """Changes line orientation if given point lies on line's left side.

        Args:
            line:  line to be changed
            point: point to be evaluated

        Returns:
            True if line orientation was changed, false if orientation was left intact,
            Resulting line
        """
    @staticmethod
    @typing.overload
    def SwapLinePoints(line: Line3D, point: Point3D) -> tuple:
        """Changes line orientation if given point lies on line's left side

        Args:
            line:  line to be changed
            point: point to be evaluated

        Returns:
            True if line orientation was changed, false if orientation was left intact,
            Resulting line
        """
    def SwapLinePoints(self):
        """ Overloaded function. See individual overloads.
        """

class ClippedSweptSolid3D():
    """Representation class for solid created by extrusion of area with borders
    of a plane at the bottom and a plane at the top in world z - axis direction
    """
    def GetBottomPlane(self) -> Plane3D:
        """Get bottom clipping plane

        Returns:
            Plane3D const reference
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point

        Returns:
            Reference point
        """
    def GetSweptArea(self) -> PolygonalArea2D:
        """Get Swept area

        Returns:
            PolygonalArea2D const reference
        """
    def GetTopPlane(self) -> Plane3D:
        """Get top clipping plane

        Returns:
            Plane3D const reference
        """
    def IsValid(self) -> bool:
        """Check if the Solid is valid

        Returns:
            True if it is a valid solid
        """
    def SetBottomPlane(self, plane: Plane3D):
        """Set bottom clipping plane

        Args:
            plane: Plane3D const reference
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set reference point

        Args:
            refPoint: New reference point
        """
    def SetSweptArea(self, area: PolygonalArea2D):
        """Set Swept area

        Args:
            area: PolygonalArea2D const reference
        """
    def SetTopPlane(self, plane: Plane3D):
        """Set top clipping plane

        Args:
            plane: Plane3D const reference
        """
    def __eq__(self, clippedSweptSolid: ClippedSweptSolid3D) -> object:
        """Comparison of clippedSweptSolids without tolerance.

        Be careful, this method work without tolerance!

        Args:
            clippedSweptSolid:Compared clippedSweptSolid.

        Returns:
            True when clippedSweptSolids are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, area: PolygonalArea2D, bottom: Plane3D, top: Plane3D):
        """Constructor which sets swept area, bottom and top planes.

        Args:
            area:   PolygonalArea3D
            bottom: Bottom Plane3D
            top:    Top Plane3D
        """
    @typing.overload
    def __init__(self, solid: ClippedSweptSolid3D):
        """Copy constructor.

        Args:
            solid: Clipped swept area solid which will be copied
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, solid: ClippedSweptSolid3D):
        """Copy constructor.

        Args:
            refPoint: reference point
            solid:    Solid which will be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix3D) -> object:
        """Matrix transformation

        Args:
            matrix: Transformation 3D matrix

        Returns:
             Transformed ClippedSweptSolid3D
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def BottomPlane(self) -> None:
        """Get and set the bottom plane as property

        :type: None
        """
    @property
    def RefPoint(self) -> None:
        """Get and set the reference point as property

        :type: None
        """
    @property
    def SweptArea(self) -> None:
        """Get and set the swept area as property

        :type: None
        """
    @property
    def TopPlane(self) -> None:
        """Get and set the top plane as property

        :type: None
        """

class ClippedSweptSolid3DList():

    def __contains__(self, value: ClippedSweptSolid3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ClippedSweptSolid3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ClippedSweptSolid3D:
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
    def __setitem__(self, index: (int | slice), value: ClippedSweptSolid3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ClippedSweptSolid3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ClippedSweptSolid3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ClosedArea2D():
    """2D closed area
    Representation class for 2D geometry closed (path bounded) area
    """
    def AddInnerCurve(self, innerpath: Path2D) -> bool:
        """Add new inner curve

        Args:
            innerpath: New inner curve ( Path2D )

        Returns:
            true if the operation was successful
        """
    def Clear(self):
        """Clear all the components of this Area
        """
    def GetInnerCurve(self, index: int) -> Path2D:
        """Get the curve of given index

        Args:
            index: Index of the inner curve

        Returns:
            const reference to the curve ( Path2D )
        """
    def GetInnerList(self) -> Path2DList:
        """Get the list of the inner curves

        Returns:
            reference to a vector that contains the inner curves ( Path2D )
        """
    def GetOuterCurve(self) -> Path2D:
        """Get the outer curve of this area

        Returns:
            const reference to outer curve ( Path2D )
        """
    def InnerCount(self) -> int:
        """Get the count of inner curves

        Returns:
            count of inner curves
        """
    def IsValid(self) -> bool:
        """Set Check the validity

        Returns:
            true if this Area is valid
        """
    def SetOuterCurve(self, outerpath: Path2D):
        """Set new Outer curve ( bounds )

        Args:
            outerpath: New outer curve ( Path2D )
        """
    def __eq__(self, closedArea: ClosedArea2D) -> object:
        """Comparison of closedAreas without tolerance.

        Be careful, this method work without tolerance!

        Args:
            closedArea:Compared closedArea.

        Returns:
            True when closedAreas are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, area: ClosedArea2D):
        """Copy constructor

        Args:
            area: Area which will be copied.
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
    def InnerList(self) -> None:
        """Get the inner path list as property

        :type: None
        """
    @property
    def OuterCurve(self) -> None:
        """Get and set the outer path as property

        :type: None
        """

class ClosedArea2DList():

    def __contains__(self, value: ClosedArea2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ClosedArea2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ClosedArea2D:
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
    def __setitem__(self, index: (int | slice), value: ClosedArea2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ClosedArea2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ClosedArea2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ClosedArea3D():
    """3D closed area
    Representation class for 3D geometry area
    """
    def AddInnerCurve(self, innerpath: Path2D) -> bool:
        """Add new inner curve

        Args:
            innerpath: New inner curve ( Path2D )

        Returns:
            true if the operation was successful
        """
    def Clear(self):
        """Clear all the components of this Profile
        """
    def GetInnerCurve(self, index: int) -> Path2D:
        """Get the curve of given index

        Args:
            index: Index of the inner curve

        Returns:
            const reference to the curve ( Path2D )
        """
    def GetInnerList(self) -> Path2DList:
        """Get the list of the inner curves

        Returns:
            reference to a vector that contains the inner curves ( Path2D )
        """
    def GetOuterCurve(self) -> Path2D:
        """Get the outer curve of this profile

        Returns:
            const reference to outer curve ( Path2D )
        """
    def GetRefPlacement(self) -> AxisPlacement3D:
        """Get axis placement

        Returns:
            const reference to the reference axis placement
        """
    def InnerCount(self) -> int:
        """Get the count of inner curves

        Returns:
            count of inner curves
        """
    def IsValid(self) -> bool:
        """Set Check the validity

        Returns:
            true if this Profile is valid
        """
    def SetOuterCurve(self, outerpath: Path2D):
        """Set new Outer curve ( bounds )

        Args:
            outerpath: New outer curve ( Path2D )
        """
    def SetRefPlacement(self, placement: AxisPlacement3D):
        """Set axis placement

        Args:
            placement: Reference axis placement
        """
    def __eq__(self, closedArea: ClosedArea3D) -> object:
        """Comparison of closedAreas without tolerance.

        Be careful, this method work without tolerance!

        Args:
            closedArea:Compared closedArea.

        Returns:
            True when closedAreas are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, closedArea: ClosedArea3D):
        """Copy constructor.

        Args:
            closedArea: 3D closed area which will be copied.
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
    def RefPlacement(self) -> None:
        """Get and set the reference placement 3d as property

        :type: None
        """

class ClosedArea3DList():

    def __contains__(self, value: ClosedArea3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ClosedArea3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ClosedArea3D:
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
    def __setitem__(self, index: (int | slice), value: ClosedArea3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ClosedArea3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ClosedArea3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ClosedAreaComposite2D():
    """2D closed area composite
    Representation class for 2D geometry closed (path bounded) area composite
    """
    def Add(self, area: ClosedArea2D) -> bool:
        """Add new area

        Args:
            area: New area

        Returns:
            true if the operation was successful
        """
    def Clear(self):
        """Clear contents of this composite
        """
    def GetProfile(self, index: int) -> ClosedArea2D:
        """Get profile from list of profiles

        Args:
            index: Index of profile in vector of profiles

        Returns:
            reference to profile
        """
    def GetProfileCount(self) -> int:
        """Get count of profiles (areas)

        Returns:
            size_t - count of profiles (areas)
        """
    def GetProfileList(self) -> ClosedArea2DList:
        """Get const reference to vector of profiles

        Returns:
            const reference to vector of profiles
        """
    def IsEmpty(self) -> bool:
        """Check if this composite has any contents ( areas )

        Returns:
            true if it is empty
        """
    def __eq__(self, closedAreaComposite: ClosedAreaComposite2D) -> object:
        """Comparison of closedAreaComposites without tolerance.

        Be careful, this method work without tolerance!

        Args:
            closedAreaComposite:Compared closedAreaComposite.

        Returns:
            True when closedAreaComposites are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, composite: ClosedAreaComposite2D):
        """Copy constructor

        Args:
            composite: Area composite which will be copied.
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
    def ProfileList(self) -> None:
        """Get the profile list as property

        :type: None
        """

class ClosedAreaComposite2DList():

    def __contains__(self, value: ClosedAreaComposite2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ClosedAreaComposite2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ClosedAreaComposite2D:
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
    def __setitem__(self, index: (int | slice), value: ClosedAreaComposite2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ClosedAreaComposite2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ClosedAreaComposite2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ClosedAreaComposite3D():
    """3D closed area composite
    Representation class for 3D geometry profile composite
    """
    def Add(self, profile: ClosedArea2D) -> bool:
        """Add new profile

        Args:
            profile: New profile

        Returns:
            true if the operation was successful
        """
    def Clear(self):
        """Clear contents of this composite
        """
    def GetClosedAreaComposite(self) -> ClosedAreaComposite2D:
        """Get constant reference to composite of ClosedArea2D

        Returns:
            ClosedAreaComposite2D
        """
    def GetRefPlacement(self) -> AxisPlacement3D:
        """Get axis placement

        Returns:
            const reference to the reference axis placement
        """
    def IsEmpty(self) -> bool:
        """Check if this composite has any contents ( profiles )

        Returns:
            true if it is empty
        """
    def SetRefPlacement(self, placement: AxisPlacement3D):
        """Set axis placement

        Args:
            placement: Reference axis placement
        """
    def __eq__(self, closedAreaComposite: ClosedAreaComposite3D) -> object:
        """Comparison of closedAreaComposites without tolerance.

        Be careful, this method work without tolerance!

        Args:
            closedAreaComposite:Compared closedAreaComposite.

        Returns:
            True when closedAreaComposites are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, composite: ClosedAreaComposite3D):
        """Copy constructor

        Args:
            composite: Profile composite which will be copied.
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
    def ClosedAreaComposite(self) -> None:
        """Get the 2d closed area composite as property

        :type: None
        """
    @property
    def RefPlacement(self) -> None:
        """Get and set the reference placement 3d as property

        :type: None
        """

class ClosedAreaComposite3DList():

    def __contains__(self, value: ClosedAreaComposite3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ClosedAreaComposite3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ClosedAreaComposite3D:
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
    def __setitem__(self, index: (int | slice), value: ClosedAreaComposite3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ClosedAreaComposite3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ClosedAreaComposite3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Clothoid2D():
    """Representation class for Clothoid2D.
    """
    def GetEndCurvature(self) -> float:
        """Get end curvature.

        Returns:
            double end curvature of clothoid.
        """
    def GetEndPoint(self) -> Point2D:
        """Get end point in world coordinate system.

        Returns:
            point Point2D.
        """
    def GetEndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system

        Returns:
            constant Point2D.
        """
    def GetIsReversed(self) -> bool:
        """is clothoid reversed

        Returns:
            true/false
        """
    def GetLength(self) -> float:
        """Get length of clothoid.

        Returns:
            double length of clothoid.
        """
    def GetParallel(self) -> float:
        """Get parallel of clothoid.

        Returns:
            double parallel of clothoid.
        """
    def GetRefPoint(self) -> Point2D:
        """Get reference point in world coordinate system

        Returns:
            point.
        """
    def GetStartCurvature(self) -> float:
        """Get start curvature.

        Returns:
            double start curvature of clothoid.
        """
    def GetStartPoint(self) -> Point2D:
        """Get start point in world coordinate system.

        Returns:
            point Point2D.
        """
    def GetStartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system

        Returns:
            constant Point2D.
        """
    def GetStartVector(self) -> Vector2D:
        """Get start vector.

        Returns:
            const Vector2D.
        """
    def GetType(self) -> eClothoidType:
        """Get type of clothoid.

        Returns:
            eClothoidType type of clothoid.
        """
    def Reverse(self):
        """Reverse orientation of the Clothoid
        """
    def Set(self, clothoid: Clothoid2D):
        """Initialize clothoid from clothoid.

        Args:
            clothoid: Clothoid2D.
        """
    def SetEndCurvature(self, curvature: float):
        """Set end curvature of clothoid.

        Args:
            curvature: end curvature of clothoid
        """
    def SetEndPoint(self, point: Point2D):
        """Set end point in world coordinate system.

        Args:
            point: const Point2D in World coordinate system.
        """
    def SetEndRelPoint(self, point: Point2D):
        """Set end point in local coordinate system

        Args:
            point: Point2D in local coordinate system
        """
    def SetLength(self, length: float):
        """Set length of clothoid.

        Args:
            length: length of clothoid.
        """
    def SetParallel(self, parallel: float):
        """Set parallel of clothoid.

        Args:
            parallel: length of clothoid.
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set reference point in world coordinate system

        Args:
            refPoint: const Point2D in World coordinate system.
        """
    def SetReversed(self, flag: bool):
        """Set orientation.

        Args:
            flag: true for reversed, false normal orientation.
        """
    def SetStartCurvature(self, curvature: float):
        """Set start curvature of clothoid.

        Args:
            curvature: start curvature of clothoid
        """
    def SetStartPoint(self, point: Point2D):
        """Set start point in world coordinate system.

        Args:
            point: const Point2D in World coordinate system.
        """
    def SetStartRelPoint(self, point: Point2D):
        """Set start point in local coordinate system

        Args:
            point: Point2D in local coordinate system
        """
    def SetStartVector(self, vec: Vector2D):
        """Set start vector.

        Args:
            vec: const Vector2D.
        """
    def SetType(self, type: eClothoidType):
        """Set type of clothoid.

        Args:
            type: type of clothoid.
        """
    def __eq__(self, clothoid: Clothoid2D) -> object:
        """Comparison of clothoids without tolerance.

        Be careful, this method work without tolerance!

        Args:
            clothoid:Compared clothoid.

        Returns:
            True when clothoids are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, clothoid: Clothoid2D):
        """Copy constructor.

        Args:
            clothoid: Clothoid2D which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix2D) -> Clothoid2D:
        """Matrix transformation.

        Args:
            matrix: transformation matrix.

        Returns:
            Clothoid2D transformed clothoid.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndCurvature(self) -> float:
        """Get end curvature.
        """
    @EndCurvature.setter
    def EndCurvature(self, curvature: float) -> None:
        """Set end curvature of clothoid.

        Args:
            curvature: end curvature of clothoid
        """
    @property
    def EndPoint(self) -> Point2D:
        """Get end point in world coordinate system.
        """
    @EndPoint.setter
    def EndPoint(self, point: Point2D) -> None:
        """Set end point in world coordinate system.

        Args:
            point: const Point2D in World coordinate system.
        """
    @property
    def EndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system
        """
    @EndRelPoint.setter
    def EndRelPoint(self, point: Point2D) -> None:
        """Set end point in local coordinate system

        Args:
            point: Point2D in local coordinate system
        """
    @property
    def Length(self) -> float:
        """Get length of clothoid.
        """
    @Length.setter
    def Length(self, length: float) -> None:
        """Set length of clothoid.

        Args:
            length: length of clothoid.
        """
    @property
    def Parallel(self) -> float:
        """Get parallel of clothoid.
        """
    @Parallel.setter
    def Parallel(self, parallel: float) -> None:
        """Set parallel of clothoid.

        Args:
            parallel: length of clothoid.
        """
    @property
    def RefPoint(self) -> Point2D:
        """Get reference point in world coordinate system
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point2D) -> None:
        """Set reference point in world coordinate system

        Args:
            refPoint: const Point2D in World coordinate system.
        """
    @property
    def StartCurvature(self) -> float:
        """Get start curvature.
        """
    @StartCurvature.setter
    def StartCurvature(self, curvature: float) -> None:
        """Set start curvature of clothoid.

        Args:
            curvature: start curvature of clothoid
        """
    @property
    def StartPoint(self) -> Point2D:
        """Get start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, point: Point2D) -> None:
        """Set start point in world coordinate system.

        Args:
            point: const Point2D in World coordinate system.
        """
    @property
    def StartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system
        """
    @StartRelPoint.setter
    def StartRelPoint(self, point: Point2D) -> None:
        """Set start point in local coordinate system

        Args:
            point: Point2D in local coordinate system
        """
    @property
    def StartVector(self) -> Vector2D:
        """Get start vector.
        """
    @StartVector.setter
    def StartVector(self, vec: Vector2D) -> None:
        """Set start vector.

        Args:
            vec: const Vector2D.
        """
    @property
    def Type(self) -> eClothoidType:
        """Get type of clothoid.
        """
    @Type.setter
    def Type(self, type: eClothoidType) -> None:
        """Set type of clothoid.

        Args:
            type: type of clothoid.
        """

class Clothoid2DList():
    """List for Clothoid2D objects
    """
    def __contains__(self, value: Clothoid2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Clothoid2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Clothoid2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Clothoid2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Clothoid2DList:
        """Add a list

        Args:
            eleList: Clothoid2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Clothoid2D):
        """Constructor with a Clothoid2D

        Args:
            ele: Clothoid2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Clothoid2D

        Args:
            eleList: Clothoid2D list
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
    def __setitem__(self, index: (int | slice), value: Clothoid2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Clothoid2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Clothoid2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Clothoid2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Comparison():
    """Utility class with methods for comparing two with each other
    """
    @staticmethod
    def AllPointsAreOneAxis(polyline: Polyline2D, tolerance: float) -> bool:
        """Check if all points of polyline are on one straight line

        Args:
            polyline:  Polyline
            tolerance: Tolerance

        Returns:
            Result of the check
        """
    @staticmethod
    @typing.overload
    def Congruent(l1p1: Point2D, l1p2: Point2D, l2p1: Point2D, l2p2: Point2D) -> bool:
        """compare 2D points of two 2D lines if are congruent

        Args:
            l1p1: the 1. point of the 1. line
            l1p2: the 2. point of the 1. line
            l2p1: the 1. point of the 2. line
            l2p2: the 2. point of the 2. line

        Returns:
            true if lines are congruent, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Congruent(l1: Line2D, l2: Line2D) -> bool:
        """compare 2D lines if are congruent

        Args:
            l1: the 1. line
            l2: the 2. line

        Returns:
            true if lines are congruent, otherwise false.
        """
    def Congruent(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(geoObject: object, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to an object.

        Args:
            geoObject: IGeometry
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(line: Line2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D line.

        Args:
            line:      2D line
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(axis: Axis2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D axis.

        Args:
            axis:      2D axis
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(polyline: Polyline2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D polyline. Returns position
        of point to the closest line of poly line

        Args:
            polyline:  2D polyline
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(arc: Arc2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D arc.

        Args:
            arc:       2D arc
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(arc: Arc3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 3D arc.

        Args:
            arc:       3D arc
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(clothoid: Clothoid2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D clothoid.

        Args:
            clothoid:  2D clothoid
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(spline: Spline2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 2D spline.

        Args:
            spline:    2D spline
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(polygon: Polygon2D, point: Point2D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a polygon 2D.

        Args:
            polygon:   Polygon2D
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eInside(inside the polygon), eOutside, eOnElement (on one of the edges), eEqualToEndPoint or Unknown
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(polygon: Polygon2D, line: Line2D) -> eComparisionResult:
        """Determine the relative position of a line to a polygon 2D.

        Args:
            polygon: Polygon2D
            line:    Line

        Returns:
            eInside(inside the polygon), eOutside, eNotParallel(the line crosses the polygon), eOnElement (on one of the edges), or Unknown
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(line: Line3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 3D line

        Args:
            line:      3D line
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(polyline: Polyline3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 3D polyline

        Args:
            polyline:  3D polyline
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(phed: Polyhedron3D, point: Point3D) -> eComparisionResult:
        """Determine the relative position of a point to a Polyhedron

        Args:
            phed:  Polyhedron
            point: Point

        Returns:
            eInside,eOutside
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(spline: Spline3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a Spline3D

        Args:
            spline:    Spline3D
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eOutside
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(spline: BSpline3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a BSpline3D

        Args:
            spline:    BSpline3D
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eOutside
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(path: Path3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a Path3D

        Args:
            path:      Path3D
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eOutside
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(b: BRep3D, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 3D BRep

        Args:
            b:         BRep3D
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eOnElement(identical to a vertes of the BRep), eInside (inside the BRep)
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(polygon1: Polygon2D, polygon2: Polygon2D) -> eComparisionResult:
        """Determine the relative position of the second polygon to the first polygon

        Args:
            polygon1: the first polygon
            polygon2: the second polygon

        Returns:
            eInside,eOutside,eCrossing
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(line: Line2D, minMax: MinMax2D) -> eComparisionResult:
        """Determine the relative position of minMax to line

        Args:
            line:   line
            minMax: minmax

        Returns:
            eOutside,eCrossing,eUnknown
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(lines: Line2DList, minMax: MinMax2D) -> eComparisionResult:
        """Determine the relative position of the minMax to lines

        Args:
            lines:  lines
            minMax: minmax

        Returns:
            eOutside,eCrossing,eUnknown
        """
    @staticmethod
    @typing.overload
    def DeterminePosition(igeo: object, point: Point3D, tolerance: float) -> eComparisionResult:
        """Determine the relative position of a point to a 3D geometry

        Args:
            igeo:      3D geometry
            point:     Point3D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            eInside,eOutside
        """
    def DeterminePosition(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def DeterminePositionEx(polyline: Polyline2D, point: Point2D, tolerance: float) -> tuple[eComparisionResult,
                            NemAll_Python_Utility.VecSizeTList]:
        """Determine the relative position of a point to a 2D polyline.

        Args:
            polyline:  2D polyline
            point:     Point
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            tuple(eOnElement(between start and end points), eEqualToStartPoint, eEqualToEndPoint, eLeft, eRight, eAbove, eBelow,
                  number of the segment of polyline in which was the point found (-1 - is not on polyline, 0 - first segm., ...))
        """
    @staticmethod
    @typing.overload
    def Equal(el1: float, el2: float) -> bool:
        """Compare two floating point numbers without tolerance

        Args:
            el1:  first number
            el2:  second number

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Point2D, el2: Point2D) -> bool:
        """Compare two 2D points without tolerance

        Args:
            el1:  first point
            el2:  second point

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Point3D, el2: Point3D) -> bool:
        """Compare two 3D points without tolerance

        Args:
            el1:  first point
            el2:  second point

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Vector2D, el2: Vector2D) -> bool:
        """Compare two 2D vectors without tolerance

        Args:
            el1:  first vector
            el2:  second vector

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Vector3D, el2: Vector3D) -> bool:
        """Compare two 3D vectors without tolerance

        Args:
            el1:  first vector
            el2:  second vector

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: float, el2: float, tol: float) -> bool:
        """Compare two floating point numbers with tolerance

        Args:
            el1:  first number
            el2:  second number
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Point2D, el2: Point2D, tol: float) -> bool:
        """Compare two 2D points with tolerance

        Args:
            el1:  first point
            el2:  second point
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Point3D, el2: Point3D, tol: float) -> bool:
        """Compare two 3D points with tolerance

        Args:
            el1:  first point
            el2:  second point
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Vector2D, el2: Vector2D, tol: float) -> bool:
        """Compare two 2D vectors with tolerance

        Args:
            el1:  first vector
            el2:  second vector
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Vector3D, el2: Vector3D, tol: float) -> bool:
        """Compare two 3D vectors with tolerance

        Args:
            el1:  first vector
            el2:  second vector
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Line2D, el2: Line2D, tol: float) -> bool:
        """Compare two 2D lines with tolerance

        Args:
            el1:  first line
            el2:  second line
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Line3D, el2: Line3D, tol: float) -> bool:
        """Compare two 3D lines with tolerance

        Args:
            el1:  first line
            el2:  second line
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Spline2D, el2: Spline2D, tol: float) -> bool:
        """Compare two 2D splines with tolerance

        Args:
            el1:  first spline
            el2:  second spline
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Clothoid2D, el2: Clothoid2D, tol: float) -> bool:
        """Compare two 2D clothoids with tolerance

        Args:
            el1:  first clothoid
            el2:  second clothoid
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Arc2D, el2: Arc2D, tol: float) -> bool:
        """Compare two 2D arcs with tolerance

        Args:
            el1:  first arc
            el2:  second arc
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Arc3D, el2: Arc3D, tol: float) -> bool:
        """Compare two 3D arcs with tolerance

        Args:
            el1:  first arc
            el2:  second arc
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: BSpline3D, el2: BSpline3D, tol: float) -> bool:
        """Compare two 3D base splines with tolerance

        Args:
            el1:  first b-spline
            el2:  second b-spline
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Spline3D, el2: Spline3D, tol: float) -> bool:
        """Compare two 3D splines with tolerance

        Args:
            el1:  first spline
            el2:  second spline
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: Polyline3D, el2: Polyline3D, tol: float) -> bool:
        """Compare two 3D polylines with tolerance

        Args:
            el1:  first polyline
            el2:  second polyline
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(el1: BSpline2D, el2: BSpline2D, tol: float) -> bool:
        """Compare two 2D base splines with tolerance

        Args:
            el1:  first b-spline
            el2:  second b-spline
            tol:  value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(path1: Path3D, path2: Path3D, tol: float) -> bool:
        """Compare two 3D paths with tolerance

        Args:
            path1:  first path
            path2:  second path
            tol:    value used to calculate allowed delta

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def Equal(igeo1: object, igeo2: object, tol: float) -> bool:
        """Compare 2 geometries with given tolerance

        Args:
            igeo1_object:  first geometry
            igeo2_object:  second geometry
            tol:           value used to calculate allowed delta

        Returns:
            true when equal
        """
    def Equal(self):
        """Compare 2 geometries with given tolerance

        Args:
            igeo1_object:  first geometry
            igeo2_object:  second geometry
            tol:           value used to calculate allowed delta

        Returns:
            true when equal
        """
    @staticmethod
    @typing.overload
    def EqualCoordsRel(el1: Point2D, el2: Point2D) -> bool:
        """compare 2 2D points using iqrkor

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualCoordsRel(el1: Point3D, el2: Point3D) -> bool:
        """compare 2 3D points using iqrkor

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    def EqualCoordsRel(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def EqualDistance(el1: Point2D, el2: Point2D, tol: float) -> bool:
        """compare 2 2D points using their distance with given tolerance

        Args:
            el1: 1. point
            el2: 2. point
            tol: tolerance

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualDistance(el1: Point3D, el2: Point3D, tol: float) -> bool:
        """compare 2 2D points using their distance with given tolerance

        Args:
            el1: 1. point
            el2: 2. point
            tol: tolerance

        Returns:
            true when equal, otherwise false.
        """
    def EqualDistance(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: float, el2: float) -> bool:
        """compare 2 doubles using built-in relative tolerance

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: float, el2: float, tol: float) -> bool:
        """compare 2 doubles using given relative tolerance

        Args:
            el1: 1. element
            el2: 2. element
            tol: relative tolerance

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: Point2D, el2: Point2D) -> bool:
        """compare 2 2D points using built-in relative tolerance

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: Point3D, el2: Point3D) -> bool:
        """compare 2 3D points using built-in relative tolerance

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: Vector2D, el2: Vector2D) -> bool:
        """compare 2 2D vectors using built-in relative tolerance

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    @staticmethod
    @typing.overload
    def EqualRel(el1: Vector3D, el2: Vector3D) -> bool:
        """compare 2 3D vectors using built-in relative tolerance

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            true when equal, otherwise false.
        """
    def EqualRel(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(geoObject: object, segment: Line2D, tolerance: float) -> int:
        """Determine the segment position of a point to a 2D geometry object

        Args:
            geoObject: IGeometry
            segment:   Line2D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(geoObject: object, point: Point3D, tolerance: float) -> int:
        """Determine the segment position of a point to a geometry object

        Args:
            geoObject: IGeometry
            point:     Point3D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(geoObject: object, point: Point2D, tolerance: float) -> int:
        """Determine the segment position of a point to a 2D geometry object

        Args:
            geoObject: IGeometry
            point:     Point2D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(line: Line2D, point: Point2D, tolerance: float) -> int:
        """Determine the segment position of a point to a Line2D

        Args:
            line:      Line2D
            point:     Point2D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(line: Line3D, point: Point3D, tolerance: float) -> int:
        """Determine the segment position of a point to a Line3D

        Args:
            line:      Line3D
            point:     Point3D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(polyPoints: PolyPoints2D, point: Point2D, tolerance: float) -> int:
        """Determine the segment position of a point to a PolyPoints<Point2D>

        Args:
            polyPoints: PolyPoints<Point2D>
            point:      Point2D
            tolerance:  tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(polygon: Polygon2D, point: Point2D, tolerance: float) -> int:
        """Determine the segment position of a point to a Polygon2D

        Args:
            polygon:   Polygon2D
            point:     Point2D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(polyPoints: PolyPoints3D, point: Point3D, tolerance: float) -> int:
        """Determine the segment position of a point to a PolyPoints<Point3D>

        Args:
            polyPoints: PolyPoints<Point3D>
            point:      Point3D
            tolerance:  tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(spline: Spline2D, point: Point2D, tolerance: float) -> int:
        """Determine the segment position of a point to a Spline2d

        Args:
            spline:    spline geo
            point:     point on spline
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(line: Line2D, segment: Line2D, tolerance: float) -> int:
        """Determine the segment position of a point to a Line2D

        Args:
            line:      Line2D
            segment:   Line2D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(line: Line3D, segment: Line3D, tolerance: float) -> int:
        """Determine the segment position of a point to a Line3D

        Args:
            line:      Line3D
            segment:   Line3D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(polyPoints: PolyPoints2D, segment: Line2D, tolerance: float) -> int:
        """Determine the segment position of a point to a PolyPoints<Point2D>

        Args:
            polyPoints: PolyPoints<Point2D>
            segment:    Line2D
            tolerance:  tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(polyPoints: PolyPoints3D, segment: Line3D, tolerance: float) -> int:
        """Determine the segment position of a point to a PolyPoints<Point3D>

        Args:
            polyPoints: PolyPoints<Point3D>
            segment:    Line3D
            tolerance:  tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    @staticmethod
    @typing.overload
    def GetSegmentNumber(geoObject: object, segment: Line3D, tolerance: float) -> int:
        """Determine the segment position of a point to a geometry object

        Args:
            geoObject: IGeometry
            segment:   Line3D
            tolerance: tolerance (if distance < tolerance, point on object)

        Returns:
            segment number 0 is first element
        """
    def GetSegmentNumber(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def HitsElement(result: eComparisionResult) -> bool:
        """Check if comparison result hits element in some way

        Args:
            result: the comparison result to check

        Returns:
            true, if the result indicates that the element is hit, otherwise false e.g. left, right, etc.
        """
    @staticmethod
    @typing.overload
    def IsInside(polygon: Polygon2D, line: Line2D) -> bool:
        """Determine if the line is inside the polygon

        Args:
            polygon: Polygon
            line:    Line

        Returns:
            true, if the line is inside the polygon
        """
    @staticmethod
    @typing.overload
    def IsInside(line: Line2D, lineToCheck: Line2D) -> bool:
        """Args:
            line
            lineToCheck
        """
    def IsInside(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def IsParallel(el1: Line2D, el2: Line2D) -> tuple[eComparisionResult, float]:
        """test 2 2D lines for parallel

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            tuple(eParallel, eAntiParallel, eNotParallel,
                  result distance)
        """
    @staticmethod
    @typing.overload
    def IsParallel(lines: Line2DList) -> eComparisionResult:
        """Check of parallelism for vector of 2D lines

        Return eAntiParallel if at least one line is antiparallel and all rest are parallel
        Return eNotParallel if at least one line is not parallel
        In all rest cases return eParallel

        Args:
            lines: - vector of 2D lines

        Returns:
            eParallel, eAntiParallel, eNotParallel
        """
    @staticmethod
    @typing.overload
    def IsParallel(el1: Line3D, el2: Line3D) -> tuple[eComparisionResult, float]:
        """test 2 3D lines for parallel

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            tuple(eParallel, eAntiParallel, eNotParallel,
                  result distance)
        """
    @staticmethod
    @typing.overload
    def IsParallel(el1: object, el2: object) -> tuple[eComparisionResult, float]:
        """test 2 Geometry object for parallel

        Args:
            el1: 1. element
            el2: 2. element

        Returns:
            tuple(eParallel, eAntiParallel, eNotParallel,
                  result distance)
        """
    def IsParallel(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def Overlapped(el1: Polyline2D, el2: Polyline2D) -> bool:
        """compare of 2 Polyline 2D

        Args:
            el1: Polyline2D
            el2: Polyline2D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(el1: Polyline3D, el2: Polyline3D, partiallyToo: bool = False) -> bool:
        """compare of 2 Polyline 3D

        Args:
            el1:          Polyline3D
            el2:          Polyline3D
            partiallyToo: First and last segment of polyline have not be identical but is enough that lies on the second polyline segments

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(pp1: PolyPoints2D, pp2: PolyPoints2D) -> bool:
        """compare of PolyPoints<Point2D>

        Args:
            pp1: PolyPoints<Point2D>
            pp2: PolyPoints<Point2D>

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(pp1: PolyPoints3D, pp2: PolyPoints3D) -> bool:
        """compare of PolyPoints<Point3D>

        Args:
            pp1: PolyPoints<Point3D>
            pp2: PolyPoints<Point3D>

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(line1: Line2D, line2: Line2D) -> bool:
        """compare of 2 2D lines

        Args:
            line1: Line2D
            line2: Line2D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(line1: Line3D, line2: Line3D, partiallyToo: bool = False) -> bool:
        """compare of 2 3D lines

        Args:
            line1:        Line3D
            line2:        Line3D
            partiallyToo: Lines have not be identical but is enough that one lies on the second

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(arc1: Arc2D, arc2: Arc2D) -> bool:
        """compare of 2 2D arcs

        Args:
            arc1: Arc2D
            arc2: Arc2D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(arc1: Arc3D, arc2: Arc3D) -> bool:
        """compare of 2 3D arcs

        Args:
            arc1: Arc3D
            arc2: Arc3D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(phed1: Polyhedron3D, phed2: Polyhedron3D) -> bool:
        """compare of 2 3D Polyhedra

        Args:
            phed1: Polyhedron3D
            phed2: Polyhedron3D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(el1: Spline2D, el2: Spline2D) -> bool:
        """compare of 2 Spline 2D

        Args:
            el1: Spline2D
            el2: Spline2D

        Returns:
            true when overlapped, otherwise false
        """
    @staticmethod
    @typing.overload
    def Overlapped(geo1: object, geo2: object) -> bool:
        """compare of 2 Geometries

        Args:
            geo1: IGeometry
            geo2: IGeometry

        Returns:
            true when overlapped, otherwise false
        """
    def Overlapped(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def signum(a: float, tol: float) -> float:
        """sgn function

        Args:
            a:   Number of which to compute sign
            tol: tolerance

        Returns:
            0, 1, -1
        """

class Cone3D():
    """3D cone
    """
    def GetApex(self) -> Point3D:
        """Get Apex of the Cone in the local coordinate system

        Returns:
            Reference to Apex.
        """
    def GetApexParent(self) -> Point3D:
        """Get Apex of the Cone in the parent coordinate system

        Returns:
            Reference to Apex.
        """
    def GetCenter(self) -> Point3D:
        """Get Center of the Cone

        Returns:
            Reference to Center.
        """
    def GetHeight(self) -> float:
        """Get Height of the Cone

        Returns:
            Reference to Height of the Cone.
        """
    def GetLocalPlacement(self) -> AxisPlacement3D:
        """Get Local Placement

        Returns:
            Reference to Local Placement.
        """
    def GetMajorRadius(self) -> float:
        """Get Major Radius of the Cone

        Returns:
            Reference to MajorRadius.
        """
    def GetMinMax(self) -> MinMax3D:
        """Get MinMax of the Cone

        Returns:
            Reference to MinMax of the Cone.
        """
    def GetMinorRadius(self) -> float:
        """Get Minor Radius of the Cone

        Returns:
            Reference to MinorRadius.
        """
    def GetXAxis(self) -> Vector3D:
        """Get X-Axis of the placement of the Cone

        Returns:
            Reference to X-Axis.
        """
    def GetZAxis(self) -> Vector3D:
        """Get Z - axis of the placement of the Cone

        Returns:
            Reference to Z-axis.
        """
    def IsCircular(self) -> bool:
        """Circularity check for the Cone

        Returns:
            true/false
        """
    def IsOblique(self) -> bool:
        """Perpendicularity check for the Cone

        Returns:
            true/false
        """
    def IsValid(self) -> bool:
        """Validity check for the Cone

        Returns:
            true/false
        """
    def SetApex(self, apex: Point3D):
        """Set Apex in the local coordinate system

        Args:
            apex: New Apex.
        """
    def SetApexParent(self, apex: Point3D):
        """Set Apex in the parent coordinate system

        Args:
            apex: New Apex.
        """
    def SetCenter(self, center: Point3D):
        """Set center

        Args:
            center: New center.
        """
    def SetHeight(self, arg2: float):
        """Set Height of the Cone

        Args:
            height: New height.
        """
    def SetLocalPlacement(self, placement: AxisPlacement3D):
        """Set Local Placement.

        Args:
            placement: Local Placement.
        """
    def SetMajorRadius(self, arg2: float):
        """Set Major Radius of the Cone

        Args:
            radius: New major radius.
        """
    def SetMinorRadius(self, arg2: float):
        """Set Minor Radius of the Cone

        Args:
            radius: New minor radius.
        """
    def __eq__(self, cone: Cone3D) -> object:
        """Comparison of cones without tolerance.

        Be careful, this method work without tolerance!

        Args:
            cone:Compared cone.

        Returns:
            True when cones are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, cone: Cone3D):
        """Copy constructor.

        Args:
            cone: Cone which will be copied.
        """
    @typing.overload
    def __init__(self, refPlacement: AxisPlacement3D, radiusMajor: float, radiusMinor: float, apex: Point3D):
        """Constructor.

        Height of the Cone is z-coordinate of the Apex.

        Args:
            refPlacement: Local Placement of the Cone.
            radiusMajor:  Major radius of the Cone.
            radiusMinor:  Minor radius of the Cone.
            apex:         Apex of the Cone
        """
    @typing.overload
    def __init__(self, radiusMajor: float, radiusMinor: float, apex: Point3D):
        """Constructor.

        Height of the Cone is z-coordinate of the Apex.

        Args:
            radiusMajor: Major radius of the Cone.
            radiusMinor: Minor radius of the Cone.
            apex:        Apex of the Cone
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
    def Apex(self) -> None:
        """Get and set the apex property

        :type: None
        """
    @property
    def LocalPlacement(self) -> None:
        """Get and set the local placement property

        :type: None
        """
    @property
    def MajorRadius(self) -> None:
        """Get and set the major radius property

        :type: None
        """
    @property
    def MinorRadius(self) -> None:
        """Get and set the minor radius property

        :type: None
        """

class Cone3DList():

    def __contains__(self, value: Cone3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Cone3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> Cone3D:
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
    def __setitem__(self, index: (int | slice), value: Cone3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Cone3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Cone3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ConicalSurface3D():
    """3D conical surface
    """
    def Get(self) -> tuple:
        """Get all surface members

        Returns:
            placement of conical surface,
            radius of conical surface in placement,
            semi angle of conical surface
        """
    def GetPlacement(self) -> AxisPlacement3D:
        """returns axis placement of the conical surface

        Returns:
             placement - point + axis vector + reference direction vector
        """
    def GetRadius(self) -> float:
        """Returns the radius at the placement

        Returns:
             radius
        """
    def GetSemiAngle(self) -> Angle:
        """Returns the value of semi angle of conical surface

        Returns:
             angle
        """
    def IsValid(self) -> bool:
        """Check surface validity

        Returns:
             bool valid = true
        """
    def Set(self, placement: AxisPlacement3D, radius: float, angle: Angle):
        """Set all surface members

        Args:
            placement: placement of conical surface
            radius:    radius of conical surface in placement
            angle:     semi angle of conical surface
        """
    def SetPlacement(self, value: AxisPlacement3D):
        """sets the position of conical surface

        Args:
            value: placement - point + axis vector + reference direction vector
        """
    def SetRadius(self, value: float):
        """Sets the radius at the placement

        Args:
            value: radius to be set
        """
    def SetSemiAngle(self, value: Angle):
        """Sets the value of semi angle of conical surface

        Args:
            value: angle to be set
        """
    def __eq__(self, surface: ConicalSurface3D) -> object:
        """Comparison of conical surfaces without tolerance.

        Be careful, this method work without tolerance!

        Args:
            conical:surface Compared conical surface.

        Returns:
            True when conical surfaces are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize"""
    @typing.overload
    def __init__(self, placement: AxisPlacement3D, radius: float, angle: Angle):
        """Default constructor.

        Args:
            placement:  placement of conical surface
            radius:     radius at a placement
            angle:      angle between placement axis and some axis on surface
        """
    @typing.overload
    def __init__(self, surface: ConicalSurface3D):
        """Copy constructor.

        Args:
            surface:  Surface which will be copied.
        """
    def __init__(self):
        """Copy constructor.

        Args:
            surface:  Surface which will be copied.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def Placement(self) -> None:
        """Get and set the placement property

        :type: None
        """
    @property
    def Radius(self) -> None:
        """Get and set the radius property

        :type: None
        """
    @property
    def SemiAngle(self) -> None:
        """Get and set the semi angle property

        :type: None
        """

class ConicalSurface3DList():

    def __contains__(self, value: ConicalSurface3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ConicalSurface3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ConicalSurface3D:
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
    def __setitem__(self, index: (int | slice), value: ConicalSurface3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ConicalSurface3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ConicalSurface3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Cuboid3D():
    """3D cuboid
    """
    def GetBottomFacePolygon(self) -> Polygon3D:
        """Get the boundary polygon of bottom face of the cuboid

        Returns:
            Bottom face boundary polygon
        """
    def GetGroundPlane(self) -> Plane3D:
        """Get ground plane ( ref point + Z-vector ).

        Returns:
            ground Plane3D.
        """
    def GetHeight(self) -> float:
        """Get height.

        Returns:
            Size of Z-vector ( vector3 ).
        """
    def GetLength(self) -> float:
        """Get length.

        Returns:
            Size of X-vector ( vector1 ).
        """
    def GetRefPoint(self) -> Point3D:
        """Get reference point.

        Returns:
            Reference point.
        """
    def GetRelStartPoint(self) -> Point3D:
        """Get start point in relative coordinates.

        Returns:
            Constant reference to the start point.
        """
    def GetStartPoint(self) -> Point3D:
        """Get start point in world coordinates.

        Returns:
            copy of start point.
        """
    def GetTopFacePolygon(self) -> Polygon3D:
        """Get the boundary polygon of top face of the cuboid

        Returns:
            Top face boundary polygon
        """
    def GetVector(self, index: int) -> Vector3D:
        """Get given vector.

        Args:
            index: Index of the vector.

        Returns:
            m_Vec[index]
        """
    def GetWidth(self) -> float:
        """Get width.

        Returns:
            Size of Y-vector ( vector2 ).
        """
    @typing.overload
    def Set(self, refPoint: Point3D, startPoint: Point3D, vec1: Vector3D, vec2: Vector3D, vec3: Vector3D):
        """Set the Cuboid.

        Args:
            refPoint:   Reference point in world coordinate system.
            startPoint: Start point of cuboid.
            vec1:       X-vector.
            vec2:       Y-vector.
            vec3:       Z-vector.
        """
    @typing.overload
    def Set(self, cuboid: Cuboid3D):
        """Initialize from cuboid.

        Args:
            cuboid: Cuboid which will be copied.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetHeight(self, height: float):
        """Set height.

        Args:
            height: New size of Z-vector ( vector3 ).
        """
    def SetLength(self, length: float):
        """Set length.

        Args:
            length: New size of X-vector ( vector1 ).
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set reference point.

        Args:
            refPoint: New reference point.
        """
    def SetStartPoint(self, startPoint: Point3D):
        """Set start point.

        Args:
            startPoint: New start point ( in world coordinates ).
        """
    def SetVector(self, vec: Vector3D, index: int):
        """Set the vector.

        Args:
            vec:   New vector.
            index: Index pf the vector.
        """
    def SetWidth(self, width: float):
        """Set width.

        Args:
            width: New size of Y-vector ( vector2 ).
        """
    def __eq__(self, cuboid: Cuboid3D) -> object:
        """Comparison of cuboids without tolerance.

        Be careful, this method work without tolerance!

        Args:
            cuboid:Compared cuboid.

        Returns:
            True when cuboids are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, cuboid: Cuboid3D):
        """Copy constructor.

        Args:
            cuboid: Cuboid which will be copied.
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, startPoint: Point3D, vec1: Vector3D, vec2: Vector3D, vec3: Vector3D):
        """Constructor.

        Args:
            refPoint:   Reference point.
            startPoint: Start point of cuboid.
            vec1:       X-vector.
            vec2:       Y-vector.
            vec3:       Z-vector
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
    def HeightVector(self) -> None:
        """Get and set the height vector property

        :type: None
        """
    @property
    def LengthVector(self) -> None:
        """Get and set the length vector property

        :type: None
        """
    @property
    def RefPoint(self) -> None:
        """Get and set the ref point property

        :type: None
        """
    @property
    def StartPoint(self) -> None:
        """Get and set the start point property

        :type: None
        """
    @property
    def WidthVector(self) -> None:
        """Get and set the width vector property

        :type: None
        """

class Cuboid3DList():

    def __contains__(self, value: Cuboid3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Cuboid3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> Cuboid3D:
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
    def __setitem__(self, index: (int | slice), value: Cuboid3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Cuboid3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Cuboid3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Cylinder3D():
    """3D cylinder
    """
    def GetApex(self) -> Point3D:
        """Get Apex of the Cylinder in the local coordinate system

        Returns:
            Reference to Apex.
        """
    def GetApexParent(self) -> Point3D:
        """Get Apex of the Cylinder in the parent coordinate system

        Returns:
            Reference to Apex.
        """
    def GetBottomCenter(self) -> Point3D:
        """Get bottom center

        Returns:
             center of bottom base
        """
    def GetCenter(self) -> Point3D:
        """Get Center of the Cylinder

        Returns:
            Reference to Center.
        """
    def GetHeight(self) -> float:
        """Get Height of the Cylinder

        Returns:
            Reference to Height of the Cylinder.
        """
    def GetLocalPlacement(self) -> AxisPlacement3D:
        """Get Local Placement

        Returns:
            Reference to Local Placement.
        """
    def GetMajorRadius(self) -> float:
        """Get Major Radius of the Cylinder

        Returns:
            Reference to Major Radius.
        """
    def GetMinMax(self) -> MinMax3D:
        """Get MinMax of the Cylinder

        Returns:
            Reference to MinMax of the Cylinder.
        """
    def GetMinorRadius(self) -> float:
        """Get Minor Radius of the Cylinder

        Returns:
            Reference to Minor Radius.
        """
    def GetSilhouetteLines(self, viewMatrix: Matrix3D, bPerspective: bool) -> Line3DList:
        """Get silhouette lines of cylinder

        Args:
            viewMatrix:   View matrix
            bPerspective: Flag if it is central projection or not (true / false)

        Returns:
            silhouette lines
        """
    def GetTopCenter(self) -> Point3D:
        """Get top center

        Returns:
             center of top plane
        """
    def GetXAxis(self) -> Vector3D:
        """Get X-Axis of the placement of the Cylinder

        Returns:
            Reference to X-Axis.
        """
    def GetYAxis(self) -> Vector3D:
        """Get Y-Axis of the placement of the Cylinder

        Returns:
            Reference to X-Axis.
        """
    def GetZAxis(self) -> Vector3D:
        """Get Z - axis of the placement of the Cylinder

        Returns:
            Reference to Z-axis.
        """
    def IsCircular(self) -> bool:
        """Circularity check of the Cylinder

        Returns:
            true/false
        """
    def IsOblique(self) -> bool:
        """Perpendicularity check of the Cylinder

        Returns:
            true/false
        """
    def IsValid(self) -> bool:
        """Validity check of the Cylinder

        Returns:
            true/false
        """
    def SetApex(self, apex: Point3D):
        """Set Apex in the local coordinate system

        Args:
            apex: New Apex.
        """
    def SetApexParent(self, apex: Point3D):
        """Set Apex in the parent coordinate system

        Args:
            apex: New Apex.
        """
    def SetCenter(self, center: Point3D):
        """Set center

        Args:
            center: New center.
        """
    def SetHeight(self, arg2: float):
        """Set Height of the Cylinder

        Args:
            height: New height.
        """
    @typing.overload
    def SetLocalPlacement(self, placement: AxisPlacement3D):
        """Set Local Placement.

        Args:
            placement: Local Placement.
        """
    @typing.overload
    def SetLocalPlacement(self, center: Point3D, xAxis: Vector3D, zAxis: Vector3D):
        """Set Local Placement.

        Args:
            center: Center point of the placement
            xAxis:  X-axis of the placement
            zAxis:  Z-axis of the placement
        """
    def SetLocalPlacement(self):
        """ Overloaded function. See individual overloads.
        """
    def SetMajorRadius(self, arg2: float):
        """Set Major Radius of the Cylinder

        Args:
            radius: New major radius.
        """
    def SetMinorRadius(self, arg2: float):
        """Set Minor Radius of the Cylinder

        Args:
            radius: New minor radius.
        """
    def __eq__(self, cylinder: Cylinder3D) -> object:
        """Comparison of cylinders without tolerance.

        Be careful, this method work without tolerance!

        Args:
            cylinder:Compared cylinder.

        Returns:
            True when cylinders are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, cylinder: Cylinder3D):
        """Copy constructor.

        Args:
            cylinder: Cylinder which will be copied.
        """
    @typing.overload
    def __init__(self, refPlacement: AxisPlacement3D, radiusMajor: float, radiusMinor: float, apex: Point3D):
        """Constructor.

        Height of the cylinder is z-coordinate of the Apex.

        Args:
            refPlacement: Local Placement of the cylinder.
            radiusMajor:  Major radius of the cylinder.
            radiusMinor:  Minor radius of the cylinder.
            apex:         Center of the Top Ellipse
        """
    @typing.overload
    def __init__(self, radiusMajor: float, radiusMinor: float, apex: Point3D):
        """Constructor.

        Height of the cylinder is z-coordinate of the Apex.

        Args:
            radiusMajor: Major radius of the cylinder.
            radiusMinor: Minor radius of the cylinder.
            apex:        Center of the Top Ellipse
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
    def Apex(self) -> None:
        """Get and set the apex property

        :type: None
        """
    @property
    def LocalPlacement(self) -> None:
        """Get and set the local placement property

        :type: None
        """
    @property
    def MajorRadius(self) -> None:
        """Get and set the major radius property

        :type: None
        """
    @property
    def MinorRadius(self) -> None:
        """Get and set the minor radius property

        :type: None
        """

class Cylinder3DList():

    def __contains__(self, value: Cylinder3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Cylinder3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> Cylinder3D:
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
    def __setitem__(self, index: (int | slice), value: Cylinder3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Cylinder3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Cylinder3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class DivisionPoints():
    """Class for DivisionPoints
    """
    def Count(self) -> int:
        """Get number of division points

        Returns:
            number of division points
        """
    def GetEndPoint(self) -> Point3D:
        """Get the end point

        Returns:
            End Point
        """
    def GetEndPointAngle(self) -> Angle:
        """Get the angle at the end point

        Returns:
            Angle at the end point
        """
    def GetPoint(self, index: int) -> Point3D:
        """Get division point

        Args:
            index: index of the division point

        Returns:
            division point as Point3D
        """
    def GetPointAngle(self, index: int) -> Angle:
        """Get the angle of a division point

        Args:
            index: index of the division point

        Returns:
            angle as Angle
        """
    def GetPointAngles(self) -> AngleList:
        """Get the angles of the division points

        Returns:
            copy of the angles of the division points as vector of Angle
        """
    def GetPoints(self) -> Point3DList:
        """Get the calculated division points

        Returns:
            copy of the division points as vector of Point3D
        """
    def GetStartPoint(self) -> Point3D:
        """Get the start point

        Returns:
            Start Point
        """
    def GetStartPointAngle(self) -> Angle:
        """Get the angle at the start point

        Returns:
            Angle at the start point
        """
    def IsSuccessful(self) -> bool:
        """Get the result of the computation

        Returns:
            Computation successful: true / false
        """
    @typing.overload
    def __init__(self, path: Path2D, sectionLength: float, eps: float):
        """Constructor

        Args:
            path:          Path to divide
            sectionLength: length of one division section
            eps:           tolerance
        """
    @typing.overload
    def __init__(self, geoObject: object, number: int, eps: float):
        """Constructor

        Args:
            geoObject: object to divide
            number:    number of division points
            eps:       tolerance
        """
    @typing.overload
    def __init__(self, path: Path2D, number: int, eps: float):
        """Constructor

        Args:
            path:   Path to divide
            number: number of division points
            eps:    tolerance
        """
    @typing.overload
    def __init__(self, geoObject: object, sectionLength: float, eps: float):
        """Constructor

        Args:
            geoObject:     object to divide
            sectionLength: length of one division section
            eps:           tolerance
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class Ellipsoid3D():
    """3D ellipsoid
    """
    def GetCenter(self) -> Point3D:
        """Get Center of the Ellipsoid

        Returns:
            Reference to Center.
        """
    def GetIsoLines(self, USegmentsCount: int, VSegmentsCount: int) -> Arc3DList:
        """Test whether the Ellipsoid is Sphere

        Args:
            USegmentsCount: count of circles
            VSegmentsCount: count of circles

        Returns:
            vector of circles
        """
    def GetLocalPlacement(self) -> AxisPlacement3D:
        """Get Local Placement

        Returns:
            Reference to Local Placement.
        """
    def GetSilhouetteContour(self, viewMatrix: Matrix3D, bPerspective: bool) -> Arc3D:
        """Get silhouette circle

        Args:
            viewMatrix:   view matrix
            bPerspective: central perspective true/false

        Returns:
            silhouette
        """
    def GetXAxis(self) -> Vector3D:
        """Get X-Axis of the placement of the Ellipsoid

        Returns:
            Reference to X-Axis.
        """
    def GetXRadius(self) -> float:
        """Get X Radius of the Ellipsoid

        Returns:
            Reference to X Radius.
        """
    def GetYAxis(self) -> Vector3D:
        """Get Y-Axis of the placement of the Ellipsoid

        Returns:
            Reference to X-Axis.
        """
    def GetYRadius(self) -> float:
        """Get Y Radius of the Ellipsoid

        Returns:
            Reference to Y Radius.
        """
    def GetZAxis(self) -> Vector3D:
        """Get Z - axis of the placement of the Ellipsoid

        Returns:
            Reference to Z-axis.
        """
    def GetZRadius(self) -> float:
        """Get Z Radius of the Ellipsoid

        Returns:
            Reference to Z Radius.
        """
    def IsSphere(self) -> bool:
        """Test whether the Ellipsoid is Sphere

        Returns:
            true/false
        """
    def IsValid(self) -> bool:
        """Validity check of the Ellipsoid

        Returns:
            true/false
        """
    def SetCenter(self, center: Point3D):
        """Set center

        Args:
            center: New center.
        """
    @typing.overload
    def SetLocalPlacement(self, placement: AxisPlacement3D):
        """Set Local Placement.

        Args:
            placement: Local Placement.
        """
    @typing.overload
    def SetLocalPlacement(self, center: Point3D, xAxis: Vector3D, zAxis: Vector3D):
        """Set Local Placement.

        Args:
            center: Center point of the placement
            xAxis:  X-axis of the placement
            zAxis:  Z-axis of the placement
        """
    def SetLocalPlacement(self):
        """ Overloaded function. See individual overloads.
        """
    def SetXRadius(self, rad: float):
        """Set X Radius of the Ellipsoid

        Args:
            rad: New radius.

        Returns:
            Reference to X Radius.
        """
    def SetYRadius(self, rad: float):
        """Set Y Radius of the Ellipsoid

        Args:
            rad: New radius
        """
    def SetZRadius(self, rad: float):
        """Set Z Radius of the Ellipsoid

        Args:
            rad: New radius
        """
    def __eq__(self, ellipsoid: Ellipsoid3D) -> object:
        """Comparison of ellipsoids without tolerance.

        Be careful, this method work without tolerance!

        Args:
            ellipsoid:Compared ellipsoid.

        Returns:
            True when ellipsoids are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ellipsoid: Ellipsoid3D):
        """Copy constructor.

        Args:
            ellipsoid: Ellipsoid which will be copied.
        """
    @typing.overload
    def __init__(self, refPlacement: AxisPlacement3D, radiusX: float, radiusY: float, radiusZ: float):
        """Constructor.

        Args:
            refPlacement: Local Placement of the ellipsoid.
            radiusX:      X radius of the Ellipsoid.
            radiusY:      Y radius of the Ellipsoid.
            radiusZ:      Z radius of the Ellipsoid.
        """
    @typing.overload
    def __init__(self, radiusX: float, radiusY: float, radiusZ: float):
        """Constructor.

        Args:
            radiusX: X radius of the Ellipsoid.
            radiusY: Y radius of the Ellipsoid.
            radiusZ: Z radius of the Ellipsoid.
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
    def LocalPlacement(self) -> None:
        """Get and set the local placement property

        :type: None
        """
    @property
    def XRadius(self) -> None:
        """Get and set the x radius property

        :type: None
        """
    @property
    def YRadius(self) -> None:
        """Get and set the y radius property

        :type: None
        """
    @property
    def ZRadius(self) -> None:
        """Get and set the z radius property

        :type: None
        """

class Ellipsoid3DList():

    def __contains__(self, value: Ellipsoid3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Ellipsoid3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> Ellipsoid3D:
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
    def __setitem__(self, index: (int | slice), value: Ellipsoid3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Ellipsoid3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Ellipsoid3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class ExtrudedAreaSolid3D():
    """Solid created by extrusion of area by given direction vector
    """
    def GetDirection(self) -> Vector3D:
        """Get direction for extrusion

        Returns:
            Vector3D const reference
        """
    def GetExtrudedArea(self) -> PolygonalArea3D:
        """Get extruded area

        Returns:
            PolygonalArea3D const reference
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point

        Returns:
            Reference point
        """
    def IsValid(self) -> bool:
        """Check if the Solid is valid

        Returns:
            True if it is a valid solid
        """
    def SetDirection(self, dir: Vector3D):
        """Set direction for extrusion

        Args:
            dir: Vector3D const reference
        """
    def SetExtrudedArea(self, area: PolygonalArea3D):
        """Set extruded area

        Args:
            area: PolygonalArea3D const reference
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set reference point

        Args:
            refPoint: New reference point
        """
    def __eq__(self, extrudedAreaSolid: ExtrudedAreaSolid3D) -> object:
        """Comparison of extrudedAreaSolids without tolerance.

        Be careful, this method work without tolerance!

        Args:
            extrudedAreaSolid:Compared extrudedAreaSolid.

        Returns:
            True when extrudedAreaSolids are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, solid: ExtrudedAreaSolid3D):
        """Copy constructor.

        Args:
            solid: Extruded area solid which will be copied
        """
    @typing.overload
    def __init__(self, solid: Point3D, refPoint: ExtrudedAreaSolid3D):
        """Copy constructor.

        Args:
            solid:    Solid which will be copied
            refPoint: reference point
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix3D) -> object:
        """Matrix transformation

        Args:
            matrix: Transformation 3D matrix
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def Direction(self) -> None:
        """Get and set the direction as property

        :type: None
        """
    @property
    def ExtrudedArea(self) -> None:
        """Get and set the extruded area as property

        :type: None
        """
    @property
    def RefPoint(self) -> None:
        """Get and set the reference point as property

        :type: None
        """

class ExtrudedAreaSolid3DList():

    def __contains__(self, value: ExtrudedAreaSolid3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: ExtrudedAreaSolid3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> ExtrudedAreaSolid3D:
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
    def __setitem__(self, index: (int | slice), value: ExtrudedAreaSolid3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: ExtrudedAreaSolid3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: ExtrudedAreaSolid3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class FaceOffset():
    """Service for offset of faces of the element
    """
    class eFaceOffsetDirection(enum.Enum):
        """Face offset direction

        eNormalDirection  : Direction of surface normal vector
        eOppositeDirection: Opposite direction to surface normal vector
        eBothSide         : In both directions
        """
        eBothSide = 2
        eNormalDirection = 0
        eOppositeDirection = 1

        names = {eNormalDirection: eNormalDirection,
                 eOppositeDirection: eOppositeDirection,
                 eBothSide: eBothSide}

        values = {0: eNormalDirection,
                  1: eOppositeDirection,
                  2: eBothSide}

        def __getitem__(self, key: (str | int | float)) -> FaceOffset.eFaceOffsetDirection:
            """ get the item for a key

            Args:
                key: value key

            Returns:
                value for the key
            """
            return self.values[key]


    def IsResultBrep(self) -> bool:
        """returns if selected object has brep geometry

        Returns:
            true if brep
        """
    def Offset(self, offsetDistance: float, direction: eFaceOffsetDirection, useOffsetStepPierce: bool, useOrthoVXSplit: bool,
               punchDirection: (Vector3D | None) = None) -> tuple[eGeometryErrorCode, typing.Any, typing.Any]:
        """Execute face offset

        Args:
            offsetDistance:      distance for offset
            direction:           offset direction 0 - in face normal direction, 1 - in both directions, 2 - opposite to face normal
            useOffsetStepPierce: if to use offset step pierce
            useOrthoVXSplit:     if to use OrthoVXSplit option
            punchDirection:      defined direction for offset (optional)

        Returns:
            tuple(eOK if success,
                  first resulting geometry,
                  second resulting geometry, set only if offset in both direction is performed)
        """
    def Shell(self, offsetDistance: float, direction: eFaceOffsetDirection, useOffsetStepPierce: bool, useOrthoVXSplit: bool,
              punchDirection: (Vector3D | None) = None) -> tuple[eGeometryErrorCode, typing.Any]:
        """Execute face shell

        Args:
            offsetDistance:      distance for offset
            direction:           offset direction 0 - in face normal direction, 1 - in both directions, 2 - opposite to face normal
            useOffsetStepPierce: if to use offset step pierce
            useOrthoVXSplit:     if to use OrthoVXSplit option
            punchDirection:      defined direction for shell (optional)

        Returns:
            tuple(eOK if success,
                  resulting geometry)
        """
    @typing.overload
    def __init__(self, inputPolyhedron: Polyhedron3D):
        """Constructor with polyhedron input geometry

        Args:
            inputPolyhedron: polyhedron to execute face offset/shell on
        """
    @typing.overload
    def __init__(self, inputPolyhedron: Polyhedron3D, faceIndices: NemAll_Python_Utility.VecSizeTList):
        """Constructor with polyhedron element

        Args:
            inputPolyhedron: polyhedron to execute face offset/shell on
            faceIndices:     vector of indices of faces to offset/shell
        """
    @typing.overload
    def __init__(self, inputBRep: BRep3D):
        """Constructor with brep element

        Args:
            inputBRep: brep to execute face offset/shell on
        """
    @typing.overload
    def __init__(self, inputBRep: BRep3D, faceIndices: NemAll_Python_Utility.VecSizeTList):
        """Constructor with brep element

        Args:
            inputBRep:   brep to execute face offset/shell on
            faceIndices: vector of indices of faces for offset/shell
        """
    @typing.overload
    def __init__(self, element: FaceOffset):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    eBothSide = eFaceOffsetDirection.eBothSide
    eNormalDirection = eFaceOffsetDirection.eNormalDirection
    eOppositeDirection = eFaceOffsetDirection.eOppositeDirection

class FilletCalculus2D():
    """Class for fillet calculation
    """
    @staticmethod
    @typing.overload
    def ClickedOnObject(line: Line2D, clickedPoint: Point2D, searchRadius: float) -> bool:
        """Check if click point is a point located on given line

        Args:
            line:         Line2D which will be checked
            clickedPoint: clicked point
            searchRadius: search radius

        Returns:
            true if point is on the line
        """
    @staticmethod
    @typing.overload
    def ClickedOnObject(arc: Arc2D, clickedPoint: Point2D, searchRadius: float) -> bool:
        """Check if click point is a point located on given arc

        Args:
            arc:          Arc2D which will be checked
            clickedPoint: clicked point
            searchRadius: search radius

        Returns:
            true if point is on the arc
        """
    def ClickedOnObject(self):
        """ Overloaded function. See individual overloads.
        """
    def GetArcHelpConstructions(self) -> Arc2DList:
        """Get all arc help constructions

        Returns:
            all arc help constructions
        """
    @staticmethod
    @typing.overload
    def GetFilletType(line1: Line2D, line2: Line2D) -> eFilletType:
        """Get fillet type for two lines

        Args:
            line1: first line
            line2: second line

        Returns:
            eFilletType
        """
    @staticmethod
    @typing.overload
    def GetFilletType(line: Line2D, arc: Arc2D) -> eFilletType:
        """Get fillet type for line and arc

        Args:
            line: line
            arc:  arc

        Returns:
            eFilletType
        """
    @staticmethod
    @typing.overload
    def GetFilletType(arc1: Arc2D, arc2: Arc2D) -> eFilletType:
        """Get fillet type for two arcs

        Args:
            arc1: first arc
            arc2: second arc

        Returns:
            eFilletType
        """
    @staticmethod
    @typing.overload
    def GetFilletType(geometry1: object, geometry2: object) -> eFilletType:
        """Get fillet type for two geometry objects

        Args:
            geometry1: first geometry element
            geometry2: second geometry element

        Returns:
            eFilletType
        """
    def GetFilletType(self):
        """ Overloaded function. See individual overloads.
        """
    def GetFillets(self) -> Arc2DList:
        """Get all possible fillets

        Returns:
            possible fillets
        """
    def GetLineHelpConstructions(self) -> object:
        """Get all line help constructions

        Returns:
            all line help constructions
        """
    def GetNearest(self, point: Point2D) -> Arc2D:
        """Get the nearest fillet to the point

        Args:
            point: Point2D

        Returns:
            nearest arc to the point
        """
    @staticmethod
    def SplitPolylineBySegment(polyline: Polyline2D, segment: int) -> tuple[Polyline2D, Polyline2D]:
        """Split polyline by given segment

        Args:
            polyline: polyline which will be split by given segment
            segment:  segment where polyline will be split

        Returns:
            tuple(firs part of polyline,
                  second part of polyline)
        """
    @staticmethod
    @typing.overload
    def TrimByHelpConstruction(line: Line2D, hcLine: Line2D, intersections: Point3DList) -> Line2D:
        """Trim line by given help construction

        Args:
            line:          which will be trimmed
            hcLine:        line help construction
            intersections: intersection points

        Returns:
            which will be trimmed
        """
    @staticmethod
    @typing.overload
    def TrimByHelpConstruction(polyline: Polyline2D, segment: Line2D, hcLine: Line2D, intersections: Point3DList) -> Polyline2D:
        """Trim polyline by given help construction

        Args:
            polyline:      which will be trimmed
            segment:       selected segment
            hcLine:        line help construction
            intersections: intersection points

        Returns:
            which will be trimmed
        """
    @staticmethod
    @typing.overload
    def TrimByHelpConstruction(arc: Arc2D, hcArc: Arc2D, intersections: Point3DList) -> Arc2D:
        """Trim arc by given help construction

        Args:
            arc:           which will be trimmed
            hcArc:         arc help construction
            intersections: intersection points

        Returns:
            which will be trimmed
        """
    def TrimByHelpConstruction(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoPolyline: Polyline2D, fillet: Arc2D, selectedGeometry: object) -> Polyline2D:
        """Update polyline geometry

        Args:
            geoPolyline:      polyline which will be updated
            fillet:           Arc2D
            selectedGeometry: selected geometry

        Returns:
            polyline which will be updated
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoPolyline: Polyline2D, fillet: Arc2D, selectedGeometry1: object, selectedGeometry2: object) -> Polyline2DList:
        """Update polyline geometry

        Args:
            geoPolyline:       polyline which will be updated
            fillet:            Arc2D
            selectedGeometry1: First selected segment
            selectedGeometry2: Second selected segment

        Returns:
            Result polylines
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoArc: Arc2D, fillet: Arc2D, selectedGeometry: object) -> Arc2D:
        """Update arc geometry

        Args:
            geoArc:           arc which will be updated
            fillet:           Arc2D
            selectedGeometry: selected geometry

        Returns:
            arc which will be updated
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoLine: Line2D, fillet: Arc2D, selectedGeometry: object) -> Line2D:
        """Update lien geometry

        Args:
            geoLine:          line which will be updated
            fillet:           Arc2D
            selectedGeometry: selected geometry

        Returns:
            line which will be updated
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoPolygon: Polygon2D, fillet: Arc2D, segment1: Line2D, segment2: Line2D, segmentCount: int = 36) -> Polygon2D:
        """Update polygon geometry

        Args:
            geoPolygon:   polygon which will be updated
            fillet:       Arc2D
            segment1:     first selected geometry
            segment2:     second selected geometry
            segmentCount: required count of segments of the polygonized fillet

        Returns:
            polygon which will be updated
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoSpline: Spline2D, fillet: Arc2D) -> Spline2D:
        """Update spline geometry

        Args:
            geoSpline: spline which will be updated
            fillet:    Arc2D

        Returns:
            spline which will be updated
        """
    @staticmethod
    @typing.overload
    def UpdateGeometry(geoPolyline: Polyline2D, fillet: Arc2D, selectedGeometry1: object, selectedGeometry2: object,
                       segmentCount: int = 36) -> Polyline2D:
        """Update polyline geometry

        Args:
            geoPolyline:       polyline which will be updated
            fillet:            Arc2D
            selectedGeometry1: the first selected geometry
            selectedGeometry2: the second selected geometry
            segmentCount:      required count of segments of the polygonized fillet

        Returns:
            polyline which will be updated
        """
    def UpdateGeometry(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, geoObj1: object, geoObj2: object, r: float):
        """constructor

        Args:
            geoObj1: IGeometry object
            geoObj2: IGeometry object
            r:       radius
        """
    @typing.overload
    def __init__(self, line1: Line2D, line2: Line2D, r: float):
        """constructor

        Args:
            line1: Line2D
            line2: Line2D
            r:     radius
        """
    @typing.overload
    def __init__(self, line: Line2D, arc: Arc2D, r: float):
        """constructor

        Args:
            line: Line2D
            arc:  Arc2D
            r:    radius
        """
    @typing.overload
    def __init__(self, arc1: Arc2D, arc2: Arc2D, r: float):
        """constructor

        Args:
            arc1: Arc2D
            arc2: Arc2D
            r:    radius
        """
    @typing.overload
    def __init__(self, arc: Arc2D, point: Point2D):
        """constructor

        Args:
            arc:   Arc2D
            point: Point2D
        """
    @typing.overload
    def __init__(self, line: Line2D, point: Point2D):
        """constructor

        Args:
            line:  Line2D
            point: Point2D
        """
    @typing.overload
    def __init__(self, element: FilletCalculus2D):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class FilletCalculus3D():
    """Class for 3D fillet calculation
    """
    @staticmethod
    @typing.overload
    def Calculate(line1: Line3D, line2: Line3D, radius: float) -> tuple[eFilletErrorCode, Line3D, Line3D, Arc3D]:
        """Calculate fillet between two coplanar 3d lines

        Args:
            line1:  first line
            line2:  second line
            radius: radius of fillet

        Returns:
            tuple(error code,
                  first line,
                  second line,
                  calculated fillet)
        """
    @staticmethod
    @typing.overload
    def Calculate(line1: Line3D, line2: Line3D) -> tuple[eFilletErrorCode, Arc3D]:
        """Calculate fillet between two parallel non collinear 3d lines.
        The end point of the first line must lie on the same plane as start point of the second line and plane is perpendicular to both lines.

        Args:
            line1: first line
            line2: second line

        Returns:
            tuple(error code,
                  calculated fillet)
        """
    @staticmethod
    @typing.overload
    def Calculate(line1: Line3D, endPoint: eLinePointIdentification, polyline: Polyline3D, startLineIndex: int, endLineIndex: int,
                  radius: float) -> tuple[eFilletErrorCode, Line3D, Line3D, Arc3D]:
        """Calculate fillet between line1 and line2. Line2 is created as line between end point of line1
        (by parameter "endPoint") and point from polyline (limited with "startPointIndex" and "endPointIndex")

        Args:
            line1:          Line 1 for fillet
            endPoint:       Sign for line2 (from where point of line1 should be start line2)
            polyline:       Polyline (buffer of end points for line2)
            startLineIndex: Start point index for polyline
            endLineIndex:   End point index for polyline
            radius:         radius of fillet

        Returns:
            tuple(error code,
                  Line 1 for fillet,
                  Line 2 from fillet calculation,
                  Calculated fillet)
        """
    @staticmethod
    @typing.overload
    def Calculate(polyhedron: Polyhedron3D, edges: NemAll_Python_Utility.VecSizeTList, radius: float,
                  propagation: bool) -> tuple[eFilletErrorCode, BRep3D]:
        """Calculate fillet on selected edges of given Polyhedron3D

        Args:
            polyhedron:  polyhedron to fillet
            edges:       edges to fillet
            radius:      fillet sphere radius
            propagation: flag for propagation of neighboring edges

        Returns:
            tuple(error code,
                  result BRep3D)
        """
    @staticmethod
    @typing.overload
    def Calculate(brep: BRep3D, radius: float) -> tuple[eFilletErrorCode, BRep3D]:
        """Calculate fillet on all edges of given BRep3D

        Args:
            brep:   brep to fillet
            radius: fillet sphere radius

        Returns:
            tuple(error code,
                  brep to fillet)
        """
    @staticmethod
    @typing.overload
    def Calculate(brep: BRep3D, edges: NemAll_Python_Utility.VecSizeTList, radius: float, propagation: bool) -> tuple[eFilletErrorCode,
                  BRep3D]:
        """Calculate fillet on selected edges of given BRep3D

        Args:
            brep:        brep to fillet
            edges:       edges to fillet
            radius:      fillet sphere radius
            propagation: flag for propagation of neighboring edges

        Returns:
            tuple(error code,
                  brep to fillet)
        """
    def Calculate(self):
        """ Overloaded function. See individual overloads.
        """
    def __init__(self):
        """Initialize
        """

class GeometryEdge():
    """Geometry edge
    Identification of any edge via point indices, not via point coordinates.
    """
    def GetEndIndex(self) -> int:
        """Get end index

        Returns:
            End index.
        """
    def GetStartIndex(self) -> int:
        """Get start index

        Returns:
            Start index.
        """
    def Set(self, edge: Kanten_t):
        """Initialize edge from old Allplan structure

        Args:
            edge: Edge which will be copied.
        """
    def SetEndIndex(self, index: int):
        """Set end index

        Index is not checked, you set anything.

        Args:
            index: End index.
        """
    def SetStartIndex(self, index: int):
        """Set start index

        Index is not checked, you set anything.

        Args:
            index: Start index.
        """
    def __eq__(self, edge: GeometryEdge) -> object:
        """Comparison of edges without tolerance.

        Be careful, this method work without tolerance!

        Args:
            edge: Compared edge.

        Returns:
            True when edges are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, startIndex: int, endIndex: int):
        """Constructor

        Args:
            startIndex: Start index of vertex.
            endIndex:   End index of vertex.
        """
    @typing.overload
    def __init__(self, edge: GeometryEdge):
        """Copy constructor

        Args:
            edge: Edge which will be copied.
        """
    @typing.overload
    def __init__(self, edge: Kanten_t):
        """Copy constructor from old Allplan structure

        Args:
            edge: Edge which will be copied.
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
    def EndIndex(self) -> None:
        """Get and set the end index property

        :type: None
        """
    @property
    def StartIndex(self) -> None:
        """Get and set the start index property

        :type: None
        """

class GeometryEdgeList():

    def __contains__(self, value: GeometryEdge) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: GeometryEdge):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> GeometryEdge:
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
    def __setitem__(self, index: (int | slice), value: GeometryEdge):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: GeometryEdge):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: GeometryEdgeList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class HealingSettings():
    """Class holding Healing settings for elements.
    """
    def GetPolygonHealingSettings(self) -> ePolygonHealingSettings:
        """Get Healing settings for polygon

        Returns:
            const Reference to Polygon healing settings
        """
    def GetPolyhedronHealingSettings(self) -> ePolyhedronHealingSettings:
        """Get Healing settings for polyhedron

        Returns:
            const Reference to Polyhedron healing settings
        """
    def IsPolygonNoModify(self) -> bool:
        """Check whether the type of the settings for polygon is PHSET_NOMODIFY

        Returns:
            true/false.
        """
    def IsPolygonNormalize(self) -> bool:
        """Check whether the type of the settings for polygon is PHSET_NOMODIFY

        Returns:
            true/false.
        """
    def IsPolyhedronNoModify(self) -> bool:
        """Check whether the type of the settings for polyhedron is HSET_NOMODIFY

        Returns:
            true/false.
        """
    def IsPolyhedronTilt(self) -> bool:
        """Check whether the type of the settings for polyhedron is HSET_TILT

        Returns:
            true/false.
        """
    def IsPolyhedronTriangulate(self) -> bool:
        """Check whether the type of the settings for polyhedron is HSET_TRIANGULATE

        Returns:
            true/false.
        """
    def IsPolyhedronUnknown(self) -> bool:
        """Check whether the type of the settings for polyhedron is HSET_TRIANGULATE

        Returns:
            true/false.
        """
    def IsWeldVerticesEnabled(self) -> bool:
        """Check if vertices welding is enabled

        Returns:
            true/false.
        """
    def SetPolygonHealingSettings(self, pgonSet: ePolygonHealingSettings):
        """Set healing settings for polygon.

        Args:
            pgonSet: new value.
        """
    def SetPolyhedronHealingSettings(self, phedSet: ePolyhedronHealingSettings):
        """Set healing settings for polyhedron.

        Args:
            phedSet: new value.
        """
    def SetWeldVertices(self, enableWeld: bool):
        """Set vertices welding

        Args:
            enableWeld: Enable vertices welding
        """
    @typing.overload
    def __init__(self, oPhedType: ePolyhedronHealingSettings = ePolyhedronHealingSettings.HSET_TRIANGULATE,
                 oPgonType: ePolygonHealingSettings = ePolygonHealingSettings.PHSET_NOMODIFY, weldVertices: bool = False):
        """Default constructor.

        Types can be found in GeometryEnums.h

        Args:
            oPhedType:    Settings for the polyhedron
            oPgonType:    Settings for the polygon
            weldVertices: Vertices welding option, if true weld vertices
        """
    @typing.overload
    def __init__(self, hSet: HealingSettings):
        """Copy constructor.

        Args:
            hSet: ApproximationSettings which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class HiddenCalculationParameters():
    """Parameters of hidden calculation.
    """
    def SetObserverMatrix(self, eyePoint: Point3D, viewPoint: Point3D):
        """Calculates observer matrix from 2 points.

        Args:
            eyePoint:  Eye point.
            viewPoint: View point.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, param: HiddenCalculationParameters):
        """Copy constructor.

        Args:
            param
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def AdjacentEdgesMaxAngle(self) -> Angle:
        """Adjacent edges max angle.

        Maximal angle in which adjacent edges will be joined.
        """
    @AdjacentEdgesMaxAngle.setter
    def AdjacentEdgesMaxAngle(self, value: Angle) -> None:
        """Adjacent edges max angle.

        Maximal angle in which adjacent edges will be joined.
        """
    @property
    def GetHiddenLines(self) -> bool:
        """Determines if get also hidden lines.

        If false only visible lines are produced during hidden calculation.
        """
    @GetHiddenLines.setter
    def GetHiddenLines(self, value: bool) -> None:
        """Determines if get also hidden lines.

        If false only visible lines are produced during hidden calculation.
        """
    @property
    def ObserverMatrix(self) -> Matrix3D:
        """Observer matrix;
        """
    @ObserverMatrix.setter
    def ObserverMatrix(self, value: Matrix3D) -> None:
        """Observer matrix;
        """

class HiddenCalculus():
    """Hidden calculation service implementation, user part.

    This template over HiddenCalculusImpl implements type safe tag storing
    for hidden calculation. It holds the vector of all used tags and convert them to
    void* needed in HiddenCalculusImpl.
    """
    def AddElement(self, elementGeometry: object, elenentMaterial: HiddenMaterial, elementTag: int):
        """Add element geometry to hidden world.

        Args:
            elementGeometry: Element geometry.
            elenentMaterial: Element material.
            elementTag:      Tag transferred over hidden calculation from element to line.
        """
    def Calculate(self):
        """Runs hidden calculation.

        \throw Exception in case of internal error.
        """
    def Configure(self, parameters: HiddenCalculationParameters):
        """Sets parameters of calculation.

        Args:
            parameters: New parameters.
        """
    def GetLinesCount(self) -> int:
        """Gets total count of lines calculated.

        \throw Exception in case of internal error and if no
               \c Calculate() was called.

        Returns:
            size_t Lines count.
        """
    def GetResultLine(self, lineIndex: int) -> tuple[Line3D, eHiddenCalculationResult]:
        """GetResultLine

        \throw Exception if index out of range.

        Args:
            lineIndex: Index of line.

        Returns:
            tuple(Line calculated by hidden itself,
                  Result of hidden for line. Hidden visible)
        """
    def GetResultLineMaterial(self, lineIndex: int) -> HiddenMaterial:
        """Gets hidden material of element line is from.

        \throw Exception if\c lineIndex out of range.

        Args:
            lineIndex: Index of line.

        Returns:
            HiddenMaterial Material.
        """
    def GetResultLineTag(self, lineIndex: int) -> int:
        """Gets (reference to) tag hooked to element line is from.

        Args:
            lineIndex: Index of line.

        Returns:
            const TagType Reference to tag object.
        """
    def __init__(self):
        """Initialize
        """

class HiddenMaterial():
    """Input element settings used by hidden calculation.
    """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, source: HiddenMaterial):
        """Copy constructor.

        Args:
            source: Source.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @property
    def ExtraSmooth(self) -> bool:
        """Extra smooth flag for entry.

        Flag is usual for elements like round column. Adjacent edges of such element
        are optimized with constant angle (20 deg) ignoring angle set in hidden
        options (usual about 1deg).
        """
    @ExtraSmooth.setter
    def ExtraSmooth(self, value: bool) -> None:
        """Extra smooth flag for entry.

        Flag is usual for elements like round column. Adjacent edges of such element
        are optimized with constant angle (20 deg) ignoring angle set in hidden
        options (usual about 1deg).
        """
    @property
    def MaterialNumber(self) -> int:
        """So called material number of entry.

        Elements with same material numbers are threaded specially depending on
        settings of hidden calculation e.g suspended lines between them etc.
        Value 0 means no material set.
        """
    @MaterialNumber.setter
    def MaterialNumber(self, value: int) -> None:
        """So called material number of entry.

        Elements with same material numbers are threaded specially depending on
        settings of hidden calculation e.g suspended lines between them etc.
        Value 0 means no material set.
        """

class IntersectRayPolyhedronFlag(enum.Enum):
    """Flag for determining the best result of ray-polyhedron intersection

    ePositiveOnly             allow only intersections with lambda >= 0
                                prefer the smallest one
    eNegativeIfNoPositive     : allow negative intersections, but only if not positive intersection can be found
                                prefer intersections with lambda close to 0
                                (i.e., prefer -1 over -2)
    eNegativePreferred        : search for the intersection with the smallest lambda
                                prefer negative over positive, prefer -2 over -1
                                (this is a simple linear comparison)
    eSmallestLmabda           : search for the intersection with the smallest lambda
    eNegativeVerticalPreferred: search for the intersection with vertical faces which are perpendicular
                                to ground plan
    """
    eNegativeIfNoPositive = 1
    eNegativePreferred = 2
    eNegativeVerticalPreferred = 4
    ePositiveOnly = 0
    eSmallestLmabda = 3

    names = {ePositiveOnly: ePositiveOnly,
             eNegativeIfNoPositive: eNegativeIfNoPositive,
             eNegativePreferred: eNegativePreferred,
             eSmallestLmabda: eSmallestLmabda,
             eNegativeVerticalPreferred: eNegativeVerticalPreferred}

    values = {0: ePositiveOnly,
              1: eNegativeIfNoPositive,
              2: eNegativePreferred,
              3: eSmallestLmabda,
              4: eNegativeVerticalPreferred}

    def __getitem__(self, key: (str | int | float)) -> IntersectRayPolyhedronFlag:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class IntersectionRayBRep():
    """Intersection result of the ray - BRep3D intersection
    """
    def __init__(self, element: IntersectionRayBRep):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def FaceIdx(self) -> int:
        """
        """
    @property
    def FaceNv(self) -> Vector3D:
        """
        """
    @property
    def IntersectionPoint(self) -> Point3D:
        """
        """

class IntersectionRayPolyhedron():
    """Intersection result of the ray - Polyhedron3D intersection
    """
    def __init__(self, element: IntersectionRayPolyhedron):
        """Copy constructor

        Args:
            element: Element to copy
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def FaceIdx(self) -> int:
        """face index of the face of the best intersection (if found, not unique) beginning from 0
        """
    @FaceIdx.setter
    def FaceIdx(self, value: int) -> None:
        """face index of the face of the best intersection (if found, not unique) beginning from 0
        """
    @property
    def FaceNv(self) -> Vector3D:
        """normal vector of best-intersected face (if found, not unique)
        """
    @FaceNv.setter
    def FaceNv(self, value: Vector3D) -> None:
        """normal vector of best-intersected face (if found, not unique)
        """
    @property
    def IntersectionPoint(self) -> Point3D:
        """intersection point (if found)
        """
    @IntersectionPoint.setter
    def IntersectionPoint(self, value: Point3D) -> None:
        """intersection point (if found)
        """
    @property
    def Lambda(self) -> float:
        """ray parameter of returned intersection (if found)
        """
    @Lambda.setter
    def Lambda(self, value: float) -> None:
        """ray parameter of returned intersection (if found)
        """
    @property
    def RetCode(self) -> int:
        """return code: 0:    no inters.,
                     1:    pos. inters. found,
                    -1:    only neg. inters. found
        """
    @RetCode.setter
    def RetCode(self, value: int) -> None:
        """return code: 0:    no inters.,
                     1:    pos. inters. found,
                    -1:    only neg. inters. found
        """

class Kanten_t():
    """old Allplan structur
    anf/end begins with 1
    """
    def __init__(self):
        """Initialize
        """
    @property
    def anf(self) -> None:
        """:type: None
        """
    @property
    def end(self) -> None:
        """:type: None
        """

class Line2D():
    """Representation class for 2D line.
    """
    def EqualRef(self, line: Line2D) -> bool:
        """Test for equal points

        Args:
            line: line for comparision

        Returns:
            True if points are equal else return false.
        """
    def Extend(self, delta: float):
        """Extend the line

        Args:
            delta: size of extension
        """
    def GetAngle(self) -> Angle:
        """Get angle of line

        Returns:
            Angle of the line
        """
    def GetCenterPoint(self) -> Point2D:
        """Get the center point in world coordinate system

        Returns:
            Center point in world coordinate system
        """
    def GetCoords(self) -> tuple[float, float, float, float]:
        """Get coordinates in world coordinate.

        Returns:
            tuple(X coordinate of start point,
                  Y coordinate of start point,
                  X coordinate of end point,
                  Y coordinate of end point)
        """
    def GetEndPoint(self) -> Point2D:
        """Get the end point in world coordinate system

        Returns:
            point.
        """
    def GetEndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system.

        Returns:
            constant point.
        """
    def GetRefPoint(self) -> Point2D:
        """Get the point.

        Returns:
            constant point.
        """
    def GetStartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.

        Returns:
            point.
        """
    def GetStartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system

        Returns:
            constant point.
        """
    def GetVector(self) -> Vector2D:
        """Get the vector.

        Returns:
            vector.
        """
    def IsPoint(self) -> bool:
        """Check, whether the line is a point (start point equal end point)

        Returns:
            Line is a point: true/false
        """
    def Reverse(self):
        """Reverse orientation of the line
        """
    @typing.overload
    def Set(self, line: Line2D):
        """Initialize line from line.

        Args:
            line: Line2D.
        """
    @typing.overload
    def Set(self, x1: float, y1: float, x2: float, y2: float):
        """Set line points in world coordinate system.

        Used world coordinates.

        Args:
            x1: X coordinate of start point.
            y1: Y coordinate of start point.
            x2: X coordinate of end point.
            y2: Y coordinate of end point.
        """
    @typing.overload
    def Set(self, point1: Point2D, point2: Point2D):
        """Set line points in world coordinate system.

        Set line from two points.
        Used world coordinates.

        Args:
            point1: Point2D start point of line.
            point2: Point2D end point of line.
        """
    @typing.overload
    def Set(self, refPoint: Point2D, point1: Point2D, point2: Point2D):
        """Set line points.

        Used local coordinate system for point1 and point2.
        refPoint used global coordinate system.

        Args:
            refPoint: refPoint point of line.
            point1:   Point2D start point of line.
            point2:   Point2D end point of line.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetEndPoint(self, endPoint: Point2D):
        """Set end point in world coordinate system.

        Args:
            endPoint: New start point.
        """
    def SetEndRelPoint(self, endPoint: Point2D):
        """Set end point in local coordinate system.

        Args:
            endPoint: New start point.
        """
    def SetRefPoint(self, refPoint: Point2D):
        """Set point in world coordinate system.

        Coordinates of points will be recalculated with new point.
        Formula: m_Points[i] = m_RefPoint + m_Points[i] - refPoint

        Args:
            refPoint: new point.
        """
    def SetStartPoint(self, startPoint: Point2D):
        """Set start point in world coordinate system.

        Args:
            startPoint: New start point.
        """
    def SetStartRelPoint(self, startPoint: Point2D):
        """Set start point in local coordinate system.

        Args:
            startPoint: New start point.
        """
    def TrimEnd(self, ds: float):
        """Trim the line at the end

        Args:
            ds:     The length by which the line will be trimmed. Negative value extends the line.

        Raises:
            ValueError: When the ds length is larger than the line's length.
        """
    def TrimStart(self, ds: float):
        """Trim the line at the start

        Args:
            ds:     The length by which the line will be trimmed. Negative value extends the line.

        Raises:
            ValueError: When the ds length is larger than the line's length.
        """
    def __eq__(self, line: Line2D) -> object:
        """Comparison of lines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            line: Compared line.

        Returns:
            True when lines are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, line: Line2D):
        """Copy constructor.

        Args:
            line: Line which will be copied.
        """
    @typing.overload
    def __init__(self, line3D: Line3D):
        """Copy constructor to convert a 3D line

        Args:
            line3D: 3D line
        """
    @typing.overload
    def __init__(self, point1: Point2D, point2: Point2D):
        """Constructor.

        Initialize line from two points. Reference point is initialized to [0.0, 0.0].
        Used world coordinates.

        Args:
            point1: Point2D start point of line.
            point2: Point2D end point of line.
        """
    @typing.overload
    def __init__(self, startPoint: Point2D, vec: Vector2D):
        """Constructor.

        Initialize line from point and relative vector to point.
        Reference point is initialized to [0.0, 0.0].
        Used world coordinates.

        Args:
            startPoint: Point2D start point of line.
            vec:        Vector2D vector of end point relative to the point1.
        """
    @typing.overload
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        """Constructor.

        Reference point is initialized to [0.0, 0.0].
        Used world coordinates.

        Args:
            x1: X coordinate of start point.
            y1: Y coordinate of start point.
            x2: X coordinate of end point.
            y2: Y coordinate of end point.
        """
    @typing.overload
    def __init__(self, refPoint: Point2D, point1: Point2D, point2: Point2D):
        """Constructor.

        Used local coordinate system for point1 and point2.
        refPoint used global coordinate system.

        Args:
            refPoint: point of line.
            point1:   start point of line.
            point2:   end point of line.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix2D) -> object:
        """Matrix transformation.

        Args:
            matrix: transformation matrix.

        Returns:
            Line2D transformed line.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndPoint(self) -> Point2D:
        """Get the end point in world coordinate system
        """
    @EndPoint.setter
    def EndPoint(self, value: Point2D) -> None:
        """Set end point in world coordinate system.
        """
    @property
    def EndRelPoint(self) -> Point2D:
        """Get the end point in relative coordinate system.
        """
    @EndRelPoint.setter
    def EndRelPoint(self, value: Point2D) -> None:
        """Set end point in local coordinate system.
        """
    @property
    def RefPoint(self) -> Point2D:
        """Get the point.


        Coordinates of points will be recalculated with new point.
        Formula: m_Points[i] = m_RefPoint + m_Points[i] - refPoint
        """
    @RefPoint.setter
    def RefPoint(self, value: Point2D) -> None:
        """Set point in world coordinate system.

        Coordinates of points will be recalculated with new point.
        Formula: m_Points[i] = m_RefPoint + m_Points[i] - refPoint
        """
    @property
    def StartPoint(self) -> Point2D:
        """Get the start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, value: Point2D) -> None:
        """Set start point in world coordinate system.
        """
    @property
    def StartRelPoint(self) -> Point2D:
        """Get the start point in relative coordinate system
        """
    @StartRelPoint.setter
    def StartRelPoint(self, value: Point2D) -> None:
        """Set start point in local coordinate system.
        """

class Line2DList():

    def __contains__(self, value: Line2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Line2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Line2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Line2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Line2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Line2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Line2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Line3D():
    """Representation class for 3D line.
    """
    def EqualRef(self, line: Line3D) -> bool:
        """Test if points are equal.

        Args:
            line: line for comparision

        Returns:
            bool
        """
    def GetCenterPoint(self) -> Point3D:
        """Get the center point in world coordinate system

        Returns:
            Center point
        """
    def GetCoords(self) -> tuple[float, float, float, float, float, float]:
        """Get the coordinates.

        Get the coordinates in world coordinate system.

        Returns:
            tuple(X coordinate of start point,
                  Y coordinate of start point,
                  Z coordinate of start point,
                  X coordinate of end point,
                  Y coordinate of end point,
                  Z coordinate of end point)
        """
    def GetEndPoint(self) -> Point3D:
        """Get the end point.

        Get the end point in world coordinate system.

        Returns:
            Point3D.
        """
    def GetEndRelPoint(self) -> Point3D:
        """Get the end point.

        Get the end point in relative coordinate system.

        Returns:
            Point3D.
        """
    def GetRefPoint(self) -> Point3D:
        """Get the point

        Returns:
            Point3D.
        """
    def GetStartPoint(self) -> Point3D:
        """Get the start point.

        Get the start point in world coordinate system.

        Returns:
            Point3D
        """
    def GetStartRelPoint(self) -> Point3D:
        """Get the start point.

        Get the start point in relative coordinate system.

        Returns:
            Point3D.
        """
    def GetVector(self) -> Vector3D:
        """Get the vector from start to end point.

        Returns:
            Vector3D.
        """
    def Is2DLine(self) -> bool:
        """Check, whether the line is a 2D line (both y coordinates are 0.)

        Returns:
            Line is a 2D line: true/false
        """
    def IsPoint(self) -> bool:
        """Check, whether the line is a point (start point equal end point)

        Returns:
            Line is a point: true/false
        """
    def Reverse(self):
        """Reverse orientation of the Line
        """
    @typing.overload
    def Set(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float):
        """Initialize from 6 doubles

        Set line points in world coordinate system

        Args:
            x1: X coordinate of start point
            y1: Y coordinate of start point
            z1: Z coordinate of start point
            x2: X coordinate of end point
            y2: Y coordinate of end point
            z2: Z coordinate of end point
        """
    @typing.overload
    def Set(self, line: Line3D):
        """Initialize line from line.

        Args:
            line: Line3D.
        """
    @typing.overload
    def Set(self, startPoint: Point3D, endPoint: Point3D):
        """Initialize from two points.

        Set line points in world coordinate system.

        Args:
            startPoint: start point.
            endPoint:   end point.
        """
    @typing.overload
    def Set(self, refPoint: Point3D, startPoint: Point3D, endPoint: Point3D):
        """Initialize from 3 points.

        Set line points in local coordinate system.

        Args:
            refPoint:   Reference point.
            startPoint: relative start point.
            endPoint:   relative end point.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetEndPoint(self, endPoint: Point3D):
        """Set end point

        Set end point in world coordinate system.

        Args:
            endPoint: End point.
        """
    def SetEndRelPoint(self, endPoint: Point3D):
        """Set end point

        Set end point in Local coordinate system.

        Args:
            endPoint: End point.
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set the point.

        Args:
            refPoint: Reference point.
        """
    def SetStartPoint(self, startPoint: Point3D):
        """Set start point

        Set start point in world coordinate system.

        Args:
            startPoint: Start point.
        """
    def SetStartRelPoint(self, startPoint: Point3D):
        """Set start point

        Set start point in Local coordinate system.

        Args:
            startPoint: Start point.
        """
    def TrimEnd(self, ds: float):
        """Trim the line at the end

        Args:
            ds:     The length by which the line will be trimmed. Negative value extends the line.

        Raises:
            ValueError: When the ds length is larger than the line's length.
        """
    def TrimStart(self, ds: float):
        """Trim the line at the start

        Args:
            ds:     The length by which the line will be trimmed. Negative value extends the line.

        Raises:
            ValueError: When the ds length is larger than the line's length.
        """
    def __eq__(self, line: Line3D) -> object:
        """Comparison of lines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            line: Compared line.

        Returns:
            True when lines are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, line2D: Line2D):
        """Copy constructor.

        Copy Line2D to Line3D at z=0.0

        Args:
            line2D: Line2D which will be copied.
        """
    @typing.overload
    def __init__(self, line: Line3D):
        """Copy constructor.

        Copy Line3D

        Args:
            line: Line3D which will be copied.
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D):
        """Constructor.

        Constructs a Line3D from point1 to point2 in world coordinates.

        Args:
            point1: start point of line.
            point2: end point of line.
        """
    @typing.overload
    def __init__(self, startPoint: Point3D, vec: Vector3D):
        """Constructor.

        Constructs a Line3D from point1 to point1+vec in world coordinates.

        Args:
            startPoint: start point of line.
            vec:        translation vector.
        """
    @typing.overload
    def __init__(self, x1: float, y1: float, z1: float, x2: float, y2: float, z2: float):
        """Constructor.

        Constructs a Line3D from 6 doubles in world coordinates.

        Args:
            x1: X coordinate of start point.
            y1: Y coordinate of start point.
            z1: Z coordinate of start point.
            x2: X coordinate of end point.
            y2: Y coordinate of end point.
            z2: Z coordinate of end point.
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, startPoint: Point3D, endPoint: Point3D):
        """Constructor.

        Constructs a Line3D in local coordinate system.

        Args:
            refPoint:   Reference point.
            startPoint: relative start point.
            endPoint:   relative end point.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> object:
        """2D matrix transformation.

        Multiplies line start and end point with matrix.

        Args:
            matrix: 2D transformation Matrix

        Returns:
            Line3D.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix3D) -> object:
        """3D matrix transformation.

        Multiplies line start and end point with matrix.

        Args:
            matrix: 3D transformation Matrix

        Returns:
            Line3D.
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndPoint(self) -> Point3D:
        """Get the end point.

        Get the end point in world coordinate system.
        """
    @EndPoint.setter
    def EndPoint(self, value: Point3D) -> None:
        """Set end point

        Set end point in world coordinate system.
        """
    @property
    def EndRelPoint(self) -> Point3D:
        """Get the end point.

        Get the end point in relative coordinate system.
        """
    @EndRelPoint.setter
    def EndRelPoint(self, value: Point3D) -> None:
        """Set end point

        Set end point in Local coordinate system.
        """
    @property
    def RefPoint(self) -> Point3D:
        """Get the point
        """
    @RefPoint.setter
    def RefPoint(self, value: Point3D) -> None:
        """Set the point.
        """
    @property
    def StartPoint(self) -> Point3D:
        """Get the start point.

        Get the start point in world coordinate system.
        """
    @StartPoint.setter
    def StartPoint(self, value: Point3D) -> None:
        """Set start point

        Set start point in world coordinate system.
        """
    @property
    def StartRelPoint(self) -> Point3D:
        """Get the start point.

        Get the start point in relative coordinate system.
        """
    @StartRelPoint.setter
    def StartRelPoint(self, value: Point3D) -> None:
        """Set start point

        Set start point in Local coordinate system.
        """

class Line3DList():

    def __contains__(self, value: Line3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Line3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Line3DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Line3D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Line3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Line3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Line3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class LineHelpConstruction():

    def __init__(self, element: LineHelpConstruction):
        """Copy constructor

        Args:
            element: Element to copy
        """
    @property
    def Line(self) -> Line2D:
        """Help construction geometry - Line2D
        """
    @Line.setter
    def Line(self, value: Line2D) -> None:
        """Help construction geometry - Line2D
        """
    @property
    def Vector(self) -> Vector2D:
        """Tangent vector
        """
    @Vector.setter
    def Vector(self, value: Vector2D) -> None:
        """Tangent vector
        """

class Matrix2D():
    """Representation class for 2D matrix

    Matrix data organization in memory:
    [0..8] indexes of array values
    0,1,  3,4 - rotation, scaling and shrinking
    6,7 - translation

    0, 1, 2,
    3, 4, 5,
    6, 7, 8

    All operations are correct only in geometry calculation context and can not be used for calculating with regular 4x4 matrix.
    """
    def AddDimension(self) -> Matrix3D:
        """Create a 3D matrix from this 2D matrix

        Returns:
            3D Matrix from this matrix
        """
    def Determinant(self) -> float:
        """Calculate determinant

        Returns:
            Determinant.
        """
    def IsIdentity(self) -> bool:
        """Check to identity matrix

        Returns:
            Return true when is matrix identity, otherwise false.
        """
    def Multiply(self, matrix: Matrix2D) -> Matrix2D:
        """Multiple matrix with given matrix

        calling " A.Multiply(B) " is identical with " A *= B "

        Args:
            matrix: Matrix to be multiple with

        Returns:
            Product of matrices
        """
    def Reflection(self, axis: Axis2D):
        """Reflection across a axis of given angle

        Args:
            axis: Reflection axis
        """
    def Reverse(self) -> bool:
        """Reverse matrix

        This method provide geometrical inverse matrix and
         can not be used with regular inverse 4x4 matrix calculations.

        Geometrical representation: Point3D = { Point3D * Matrix } * Matrix.Reverse()

        Returns:
            True when operation is successful, otherwise false.
        """
    def Rotation(self, point: Point2D, angle: Angle):
        """Rotate the matrix

        Args:
            point: Point of rotation
            angle: Angle of rotation.
        """
    def Scaling(self, scaleX: float, scaleY: float):
        """Scale the matrix

        Args:
            scaleX: Scale in X axis.
            scaleY: Scale in Y axis.
        """
    def SetIdentity(self):
        """Initialize identity matrix
        """
    def SetReflection(self, axis: Axis2D):
        """Initialize matrix only with reflection

        Args:
            axis: Reflection axis
        """
    def SetRotation(self, point: Point2D, angle: Angle):
        """Initialize matrix only with rotation

        Args:
            point: Point of rotation.
            angle: Angle of rotation.
        """
    def SetScaling(self, scaleX: float, scaleY: float):
        """Initialize matrix only with scaling factors

        Args:
            scaleX: Scale in X axis.
            scaleY: Scale in Y axis.
        """
    def SetTranslation(self, vec: Vector2D):
        """Initialize matrix only with translation

        Args:
            vec: Vector of translation.
        """
    def SetValue(self, index: int, value: float) -> bool:
        """Set the matrix element at a specified position

        Use this method when you don't want to catch exception by operator[].

        Args:
            index: Position index <0..9>
            value: Value for set

        Returns:
            True when operation successful (index is not out of range), otherwise false.
        """
    def Translate(self, vec: Vector2D):
        """Translate the matrix

        Args:
            vec: Vector of translation.
        """
    def __add__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix addition

        Formula: Result(new matrix) = A+B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __getitem__(self, index: int) -> float:
        """Get the matrix element at a specified position

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: Position index <0..9>

        Returns:
            Returns an element at a specified position.
        """
    def __iadd__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix addition

        Formula: A += B  or A = A+B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __imul__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix multiplication

        Formula: A *= B  or A = A*B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Product of matrices
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, matrix: Matrix2D):
        """Copy constructor

        Args:
            matrix: Matrix which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix addition

        Formula: A -= B  or A = A-B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __mul__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix multiplication

        Formula: Result(new matrix) = A*B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Product of matrices
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    def __sub__(self, matrix: Matrix2D) -> Matrix2D:
        """Matrix addition

        Formula: Result(new matrix) = A-B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """

class Matrix3D():
    """Representation class for 3D matrix

    Matrix data organization in memory:
    [0..15] indexes of array values
    0,1,2,  4,5,6,  8,9,10 - rotation, scaling and shrinking
    12,13,14 - translatio

    0, 1, 2, 3   
    4, 5, 6, 7   
    8, 9, 10,11  
    12,13,14,15  

    All operations are correct only in geometry calculation context and can not be used for calculating with regular 4x4 matrix.
    """
    def Determinant(self) -> float:
        """Calculate determinant

        Returns:
            Determinant.
        """
    def GaussInvert(self) -> bool:
        """Inverse matrix by Gauss

        Returns:
            True when operation is successful, otherwise false.
        """
    def GetScaleX(self) -> float:
        """Get scale X

        Returns:
            scale X
        """
    def GetScaleY(self) -> float:
        """Get scale Y

        Returns:
            scale Y
        """
    def GetScaleZ(self) -> float:
        """Get scale Z

        Returns:
            scale Z
        """
    def GetScaling(self) -> tuple[float, float, float]:
        """Calculates the scaling factors from the matrix

        Returns:
            tuple(Scale in X axis,
                  Scale in Y axis,
                  Scale in Z axis)
        """
    def GetTranslationVector(self) -> Vector3D:
        """Get translation part of a matrix

        Returns:
            The vector of translation
        """
    def GetVectorX(self) -> Vector3D:
        """Get vector X

        Returns:
            Vector X
        """
    def GetVectorY(self) -> Vector3D:
        """Get vector Y

        Returns:
            Vector Y
        """
    def GetVectorZ(self) -> Vector3D:
        """Get vector Z

        Returns:
            Vector Z
        """
    def IsIdentity(self) -> bool:
        """Check to identity matrix

        Returns:
            Return true when is matrix identity, otherwise false.
        """
    def LaplaceTransform(self):
        """Transformation matrix by Laplace
        """
    def Multiply(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix multiplication

        Formula: A *= B  or A = A*B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Product of matrices
        """
    def ReduceZDimension(self) -> Matrix2D:
        """Create a 2D matrix from this 3D matrix

        Returns:
            a 2D matrix from this 3D matrix
        """
    def Reflection(self, plane: Plane3D):
        """Reflection across a plane

        Args:
            plane: Reflection plane
        """
    def Reverse(self) -> bool:
        """Reverse matrix

        This method provide geometrical inverse matrix and
         can not be used with regular inverse 4x4 matrix calculations.

        Geometrical representation: Point3D = { Point3D * Matrix } * Matrix.Reverse()

        Returns:
            True when operation is successful, otherwise false.
        """
    def Rotation(self, line: Line3D, angle: Angle) -> bool:
        """Rotate the matrix

        Rotate current matrix, not created new one.

        Args:
            line:  Axis of rotation.
            angle: Angle of rotation.

        Returns:
            True when successful, otherwise false.
        """
    def Scaling(self, scaleX: float, scaleY: float, scaleZ: float):
        """Scale the matrix

        Scale current matrix, not created new one.

        Args:
            scaleX: Scale in X axis.
            scaleY: Scale in Y axis.
            scaleZ: Scale in Z axis.
        """
    def SetIdentity(self):
        """Initialize identity matrix
        """
    def SetProjection(self, proj: eProjectionMatrixType):
        """Create a matrix for the required projection

        Method throw THROW_GEO_EXCEPTION_INCORRECT_PARAMETERS_ geometry exception in case of invalid proj.

        Args:
            proj: The required projection
        """
    def SetReflection(self, plane: Plane3D):
        """Initialize matrix only with reflection

        Args:
            plane: Reflection plane
        """
    @typing.overload
    def SetRotation(self, axis: Line3D, angle: Angle) -> bool:
        """Initialize matrix only with rotation

        Args:
            axis:  Axis of rotation.
            angle: Angle of rotation.

        Returns:
            True when successful, otherwise false.
        """
    @typing.overload
    def SetRotation(self, startDirection: Vector3D, endDirection: Vector3D) -> bool:
        """Initialize matrix only with rotation defined by start and end direction vectors

        Args:
            startDirection: direction vector for start of rotation.
            endDirection:   direction vector for end of rotation.

        Returns:
            True when successful, otherwise false.
        """
    def SetRotation(self):
        """ Overloaded function. See individual overloads.
        """
    def SetScaling(self, scaleX: float, scaleY: float, scaleZ: float):
        """Initialize matrix only with scaling factors

        Args:
            scaleX: Scale in X axis.
            scaleY: Scale in Y axis.
            scaleZ: Scale in Z axis.
        """
    def SetTranslation(self, vec: Vector3D):
        """Initialize matrix only with translation

        Args:
            vec: Vector of translation.
        """
    def SetValue(self, index: int, value: float) -> bool:
        """Set the matrix element at a specified position

        Use this method when you don't want to catch exception by operator[].

        Args:
            index: Position index <0..15>
            value: Value for set

        Returns:
            True when operation successful (index is not out of range), otherwise false.
        """
    def SetValues(self, v00: float, v01: float, v02: float, v03: float, v10: float, v11: float, v12: float, v13: float, v20: float,
                  v21: float, v22: float, v23: float, v30: float, v31: float, v32: float, v33: float):
        """Sets each matrix-element

        Args:
            v00: first row, first element
            v01: first row, second element
            v02: first row, third element
            v03: first row, fourth element
            v10: second row, first element
            v11: second row, second element
            v12: second row, third element
            v13: second row, fourth element
            v20: third row, first element
            v21: third row, second element
            v22: third row, third element
            v23: third row, fourth element
            v30: fourth row, first element
            v31: fourth row, second element
            v32: fourth row, third element
            v33: fourth row, fourth element
        """
    def Translate(self, vec: Vector3D):
        """Translate the matrix

        Args:
            vec: Vector of translation.
        """
    def Transpose(self):
        """Transpose matrix

         All transform-services multiply transformation-matrix from the right side:
         If you need the result as it would be multiplication from the left side you
         need the transposed Matrix

         [x,y,z,1.0] x /  0, 1, 2, 3\         /  0, 1, 2, 3\      / x
                       |  4, 5, 6, 7 |         |  4, 5, 6, 7 |  x   | y |
                       |  8, 9,10,11 |         |  8, 9,10,11 |      | z |
                      \ 12,13,14,15 /        \ 12,13,14,15 /     \1.0/

             moving-part: 12,13,14              moving-part: 3, 7, 11
        """
    def __add__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix addition

        Formula: Result(new matrix) = A+B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __eq__(self, mat: Matrix3D) -> bool:
        """Comparison of matrices without tolerance.

        Be careful, this method work without tolerance!

        Args:
            arc: Compared arc.

        Returns:
            True when matrices are equal, otherwise false.
        """
    def __getitem__(self, index: int) -> float:
        """Get the matrix element at a specified position

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index: Position index <0..15>

        Returns:
            Returns an element at a specified position.
        """
    def __iadd__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix addition

        Formula: A += B  or A = A+B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __imul__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix multiplication

        Formula: A *= B  or A = A*B.
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Product of matrices
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, proj: eProjectionMatrixType):
        """Constructor

        Create a matrix for the required projection.

        Args:
            proj: The required projection
        """
    @typing.overload
    def __init__(self, matrix: Matrix3D):
        """Copy constructor

        Args:
            matrix: Matrix which will be copied.
        """
    @typing.overload
    def __init__(self, v00: float, v01: float, v02: float, v03: float, v10: float, v11: float, v12: float, v13: float, v20: float,
                 v21: float, v22: float, v23: float, v30: float, v31: float, v32: float, v33: float):
        """Constructor setting each matrix-element

        Args:
            v00: first row, first element
            v01: first row, second element
            v02: first row, third element
            v03: first row, fourth element
            v10: second row, first element
            v11: second row, second element
            v12: second row, third element
            v13: second row, fourth element
            v20: third row, first element
            v21: third row, second element
            v22: third row, third element
            v23: third row, fourth element
            v30: fourth row, first element
            v31: fourth row, second element
            v32: fourth row, third element
            v33: fourth row, fourth element
        """
    @typing.overload
    def __init__(self, valuesinrows: list):
        """Constructor

        Args:
            valuesinrows: matrix values by rows as Python list
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix addition

        Formula: A -= B  or A = A-B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """
    def __mul__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix multiplication

        Formula: Result(new matrix) = A*B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Product of matrices
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    def __sub__(self, matrix: Matrix3D) -> Matrix3D:
        """Matrix addition

        Formula: Result(new matrix) = A-B
        A is this matrix.

        Args:
            matrix: B matrix

        Returns:
            Addition of matrices
        """

class Matrix3DList():
    """List for Matrix3D objects
    """
    def __contains__(self, value: Matrix3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Matrix3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Matrix3DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Matrix3D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Matrix3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Matrix3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Matrix3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class MinMax2D():
    """Representation class for 2D MinMax box.
    """
    @typing.overload
    def Deflate(self, x: float, y: float):
        """ Deflate in x and y axis.

        Args:
            x
            y
        """
    @typing.overload
    def Deflate(self, size: float):
        """ Deflate in x,y axis concurrently.

        Args:
            size
        """
    def Deflate(self):
        """ Overloaded function. See individual overloads.
        """
    def Get(self) -> tuple[Point2D, Point2D]:
        """Get minimum and maximum point

        Returns:
            tuple(minimum point,
                  maximum point)
        """
    def GetCenter(self) -> Point2D:
        """Get box center point

        Returns:
            center point
        """
    def GetMax(self) -> Point2D:
        """Get maximum point

        Returns:
            maximum point
        """
    def GetMin(self) -> Point2D:
        """Get minimum point

        Returns:
            minimum point
        """
    def GetSizeX(self) -> float:
        """Get the size of the box in the X direction

        Returns:
            delta X value
        """
    def GetSizeY(self) -> float:
        """Get the size of the box in the Y direction

        Returns:
            delta Y value
        """
    @typing.overload
    def Inflate(self, x: float, y: float):
        """ ame Inflate and deflate minmax box

        Inflate in x and y axis.

        Args:
            x
            y
        """
    @typing.overload
    def Inflate(self, size: float):
        """ Inflate in x,y axis concurrently.

        Args:
            size
        """
    def Inflate(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def IsContaining(self, box: MinMax2D) -> bool:
        """Is box inside this box

        Args:
            box: Potentially contained box

        Returns:
            true, if is inside, otherwise false
        """
    @typing.overload
    def IsContaining(self, point: Point2D) -> bool:
        """Is point inside this box

        Args:
            point: point in world coordinate system

        Returns:
            true, if is inside, otherwise false
        """
    def IsContaining(self):
        """ Overloaded function. See individual overloads.
        """
    def IsValid(self) -> bool:
        """Test if box is valid

        Returns:
            true, if box valid, otherwise false
        """
    def Overlaps(self, box: MinMax2D) -> bool:
        """Does box overlap this box

        Args:
            box: Box

        Returns:
            true, if boxes overlap, otherwise false
        """
    def Reset(self):
        """Set min point to [DBL_MAX,DBL_MAX]
        and max point to [-DBL_MAX,-DBL_MAX]
        """
    def Set(self, min: Point2D, max: Point2D):
        """Set minimum and maximum point

        Args:
            min: minimum point
            max: maximum point
        """
    def SetMax(self, max: Point2D):
        """Set maximum point

        Args:
            max: maximum point
        """
    def SetMin(self, min: Point2D):
        """Set minimum point

        Args:
            min: minimum point
        """
    def ToPolygon2D(self) -> tuple[bool, Polygon2D]:
        """Creates a 2D polygon from the minmax box the corners of MinMax.

        Returns:
            tuple(true, if the polygon has been created successfully, otherwise false,
                  polygon created from the minmax box)
        """
    def __add__(self, minmax: MinMax2D) -> MinMax2D:
        """Expand MinMax2D box.

        Expands the MinMax2D box by the box given in parameter minmax

        Args:
            minmax: MinMax2D to be added

        Returns:
            minmax box.
        """
    def __eq__(self, minmax: MinMax2D) -> object:
        """Comparison of minmax objects without tolerance.

        Be careful, this method work without tolerance!

        Args:
            minmax: Compared minmax.

        Returns:
            True when minmax objects are equal, otherwise false.
        """
    def __getitem__(self, index: int) -> Point2D:
        """Get the corners of MinMax.
        Corner index (0-left bottom, 1-right bottom, 2-right top, 3-left top)

        This method is checked and throwing Geometry::Exception when index is out of range.

        Args:
            index

        Returns:
            corner as Point2D in world coordinate system.
        """
    @typing.overload
    def __iadd__(self, minmax: MinMax2D) -> MinMax2D:
        """Expand MinMax2D box.

        Expands the MinMax2D box by the box given in parameter minmax

        Args:
            minmax: MinMax2D to be added

        Returns:
            minmax box.
        """
    @typing.overload
    def __iadd__(self, point: Point2D) -> MinMax2D:
        """Expand MinMax2D box.

        Expands the MinMax2D box by the Point2D given in parameter point

        Args:
            point: Point2D to be added

        Returns:
            minmax box.
        """
    @typing.overload
    def __iadd__(self, box: BoundingBox2D) -> MinMax2D:
        """Expand MinMax2D box.

        Expands the MinMax2D box by the bounding box given in parameter box

        Args:
            box: Bounding box to be added

        Returns:
            minmax box.
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, min: Point2D, max: Point2D):
        """Set constructor

        Initialize MinMax box with given MIN and MAX points.

        Args:
            min: minimum point
            max: maximum point
        """
    @typing.overload
    def __init__(self, point: Point2D):
        """Set constructor

        Initialize MinMax box with given point.

        Args:
            point: point
        """
    @typing.overload
    def __init__(self, minmax: MinMax2D):
        """Copy constructor.

        Args:
            minmax: MinMax2D to be copied
        """
    @typing.overload
    def __init__(self, minmax: MinMax3D):
        """Copy constructor.

        Args:
            minmax: the MinMax3D box to be copied into MinMax2D. Only X and Y values will be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Max(self) -> Point2D:
        """Get maximum point
        """
    @Max.setter
    def Max(self, value: Point2D) -> None:
        """Set maximum point
        """
    @property
    def Min(self) -> Point2D:
        """Get minimum point
        """
    @Min.setter
    def Min(self, value: Point2D) -> None:
        """Set minimum point
        """
    @property
    def SizeX(self) -> float:
        """Get the size of the box in the X direction
        """
    @property
    def SizeY(self) -> float:
        """Get the size of the box in the Y direction
        """

class MinMax2DList():
    """List for MinMax2D objects
    """
    def __contains__(self, value: MinMax2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: MinMax2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: MinMax2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> MinMax2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: MinMax2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: MinMax2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: MinMax2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class MinMax3D():
    """Representation class for 3D MinMax box.
    """
    @typing.overload
    def Deflate(self, size: float):
        """ Deflate in x,y,z axis concurrently.

        Args:
            size
        """
    @typing.overload
    def Deflate(self, x: float, y: float, z: float):
        """ Deflate in x, y and z axis.

        Args:
            x
            y
            z
        """
    def Deflate(self):
        """ Overloaded function. See individual overloads.
        """
    def Get(self) -> tuple[Point3D, Point3D]:
        """Get minimum and maximum point

        Returns:
            tuple(minimum point,
                  maximum point)
        """
    def GetCenter(self) -> Point3D:
        """Get box center point

        Returns:
            center point
        """
    def GetMax(self) -> Point3D:
        """Get maximum point

        Returns:
            maximum point
        """
    def GetMin(self) -> Point3D:
        """Get minimum point

        Returns:
            minimum point
        """
    def GetSizeX(self) -> float:
        """Get the size of the box in the X direction

        Returns:
            delta X value
        """
    def GetSizeY(self) -> float:
        """Get the size of the box in the Y direction

        Returns:
            delta Y value
        """
    def GetSizeZ(self) -> float:
        """Get the size of the box in the Y direction

        Returns:
            delta Y value
        """
    @typing.overload
    def Inflate(self, x: float, y: float, z: float):
        """ ame Inflate and deflate minmax box

        Inflate in x, y and z axis.

        Args:
            x
            y
            z
        """
    @typing.overload
    def Inflate(self, size: float):
        """ Inflate in x,y,z axis concurrently.

        Args:
            size
        """
    def Inflate(self):
        """ Overloaded function. See individual overloads.
        """
    def IsContaining(self, box: MinMax3D) -> bool:
        """Is box inside this box

        Args:
            box: Potentially contained box

        Returns:
            true, if is inside, otherwise false
        """
    def IsValid(self) -> bool:
        """Test if box is valid

        Returns:
            true, if box valid, otherwise false
        """
    def Overlaps(self, box: MinMax3D) -> bool:
        """Does box overlap this box

        Args:
            box: Box

        Returns:
            true, if boxes overlap, otherwise false
        """
    def Reset(self):
        """Set min point to [DBL_MAX,DBL_MAX,DBL_MAX]
        and max point to [-DBL_MAX,-DBL_MAX,-DBL_MAX]
        """
    def Set(self, min: Point3D, max: Point3D):
        """Set minimum and maximum point

        Args:
            min: minimum point
            max: maximum point
        """
    def SetMax(self, max: Point3D):
        """Set maximum point

        Args:
            max: maximum point
        """
    def SetMin(self, min: Point3D):
        """Set minimum point

        Args:
            min: minimum point
        """
    def __add__(self, minmax: MinMax3D) -> MinMax3D:
        """Expand MinMax3D box.

        Expands the MinMax3D box by the box given in parameter minmax

        Args:
            minmax: MinMax3D to be added

        Returns:
            minmax box.
        """
    def __eq__(self, minmax: MinMax3D) -> object:
        """Comparison of minmax objects without tolerance.

        Be careful, this method work without tolerance!

        Args:
            minmax: Compared minmax.

        Returns:
            True when minmax objects are equal, otherwise false.
        """
    @typing.overload
    def __iadd__(self, minmax: MinMax3D) -> MinMax3D:
        """Expand MinMax3D box.

        Expands the MinMax3D box by the box given in parameter minmax

        Args:
            minmax: MinMax3D to be added

        Returns:
            minmax box.
        """
    @typing.overload
    def __iadd__(self, point: Point3D) -> MinMax3D:
        """Expand MinMax3D box.

        Expands the MinMax3D box by the Point3D given in parameter point

        Args:
            point: Point3D to be added

        Returns:
            minmax box.
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, min: Point3D, max: Point3D):
        """Set constructor

        Initialize MinMax box with given MIN and MAX points.

        Args:
            min: minimum point
            max: maximum point
        """
    @typing.overload
    def __init__(self, point: Point3D):
        """Set constructor

        Initialize MinMax box with given point.

        Args:
            point: point
        """
    @typing.overload
    def __init__(self, minmax: MinMax3D):
        """Copy constructor.

        Args:
            minmax: MinMax3D to be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Max(self) -> Point3D:
        """Get maximum point
        """
    @Max.setter
    def Max(self, value: Point3D) -> None:
        """Set maximum point
        """
    @property
    def Min(self) -> Point3D:
        """Get minimum point
        """
    @Min.setter
    def Min(self, value: Point3D) -> None:
        """Set minimum point
        """
    @property
    def SizeX(self) -> float:
        """Get the size of the box in the X direction
        """
    @property
    def SizeY(self) -> float:
        """Get the size of the box in the Y direction
        """
    @property
    def SizeZ(self) -> float:
        """Get the size of the box in the Y direction
        """

class Offset3DPlane(enum.Enum):
    """Definition of plane on which offset of 3D elements will be calculated

    eNoPlane: No plane defined
    eXY     : Plane defined by X and Y axis
    eXZ     : Plane defined by X and Z axis
    eYZ     : Plane defined by Y and Z axis
    """
    eNoPlane = 0
    eXY = 1
    eXZ = 2
    eYZ = 3

    names = {eNoPlane: eNoPlane,
             eXY: eXY,
             eXZ: eXZ,
             eYZ: eYZ}

    values = {0: eNoPlane,
              1: eXY,
              2: eXZ,
              3: eYZ}

    def __getitem__(self, key: (str | int | float)) -> Offset3DPlane:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class OrientedEdge():
    """Oriented edge
    Identification of any edge via edge handle and orientation (positive, negative).
    """
    def GetEdgeHandle(self) -> int:
        """Get handle to the edge

        Returns:
            Edge handle.
        """
    def HasPositiveOrientation(self) -> bool:
        """Get the flag of positive orientation.

        Returns:
            True when edge have positive orientation, otherwise false.
        """
    @typing.overload
    def Set(self, orientedEdge: OrientedEdge):
        """Initialize edge from old Allplan structure

        Args:
            orientedEdge: Edge which will be copied.
        """
    @typing.overload
    def Set(self, edgeHandle: int, positiveOrientation: bool):
        """Set edge handle and orientation

        Handle is not checked, you set anything.

        Args:
            edgeHandle:          Handle to the edge which will be set.
            positiveOrientation: Set true when orientation is positive, otherwise false.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetEdgeHandle(self, edgeHandle: int):
        """Set handle to the edge

         edgeHandle is not checked, you set anything.

        Args:
            edgeHandle: Handle to the edge which will be set.
        """
    def SetOrientation(self, positiveOrientation: bool):
        """Set orientation

        Args:
            positiveOrientation: Set true when orientation is positive, otherwise false.
        """
    def __eq__(self, orientedEdge: OrientedEdge) -> object:
        """Equal operator

        Args:
            orientedEdge: Edge to comparison

        Returns:
            True when both edges are equal.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, edgeHandle: int, positiveOrientation: bool):
        """Constructor

        Args:
            edgeHandle:          Set edge handle.
            positiveOrientation: Set orientation, true for positive, false for negative
        """
    @typing.overload
    def __init__(self, orientedEdge: OrientedEdge):
        """Copy constructor

        Args:
            orientedEdge: Edge which will be copied.
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
    def EdgeHandle(self) -> None:
        """Get and set the edge handle property

        :type: None
        """
    @property
    def Positive(self) -> None:
        """Get and set the positive orientation property

        :type: None
        """

class OrientedEdgeList():

    def __contains__(self, value: OrientedEdge) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: OrientedEdge):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> OrientedEdge:
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
    def __setitem__(self, index: (int | slice), value: OrientedEdge):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: OrientedEdge):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: OrientedEdgeList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Path():

    def Clear(self):
        """Clear all geometries from path
        """
    def Count(self) -> int:
        """Count of geometries stored in path

        Returns:
            Count of geometries.
        """
    def GetElement(self, arg2: int) -> object:
        """Get the element by index

        Args:
            index: Element index.

        Returns:
            Element
        """
    def IsEmpty(self) -> bool:
        """Tests whether no elements are present

        Returns:
            True for an empty, otherwise false.
        """
    def Remove(self, position: int) -> eGeometryErrorCode:
        """Remove geometry at the specified position

        Args:
            position: Specified position of removed geometry.

        Returns:
            Error code.
        """
    def Reverse(self):
        """Reverse orientation of the PathElement
        """
    def __iter__(self) -> PathIterator:
        """Get the iterator
        """

class Path2D(Path):
    """Representation class for 2D path.
    """
    @typing.overload
    def Add(self, element: Path2D) -> eGeometryErrorCode:
        """Add element into path Path2D

        Args:
            element: Path element to add

        Returns:
            error code
        """
    @typing.overload
    def Add(self, element_object: object) -> eGeometryErrorCode:
        """Add element into path Path2D

        Args:
            element_object: Pointer to element to add

        Returns:
            error code
        """
    def Add(self):
        """ Overloaded function. See individual overloads.
        """
    def GetEndPoint(self) -> Point2D:
        """Get path end point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Returns:
            const Point2D End point
        """
    def GetEndRelPoint(self) -> Point2D:
        """Get relative end (last) point of the path

        Returns:
            End point (relative)
        """
    def GetStartPoint(self) -> Point2D:
        """Get path start point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Returns:
            const Point2D Start point
        """
    def GetStartRelPoint(self) -> Point2D:
        """Get relative start (first) point of the path

        Returns:
            Start point (relative)
        """
    def IsClosed(self) -> bool:
        """Check for closed path, it mean that first point is same as last point

        Returns:
            True when path is closed, otherwise false.
        """
    def IsItPossibleToAddElement(self, pGeometry_object: object) -> bool:
        """Check if the geometry can be added into path Path2D

        Args:
            pGeometry_object: Pointer to geometry to check
        """
    def IsValid(self) -> bool:
        """Validity check

        \warning Path doesn't have to be closed to be valid, you have to check this extra
        """
    @staticmethod
    def IsValidCurveType(pGeometry_object: object) -> bool:
        """Check if the geometry is supported by Path2D

        Args:
            pGeometry_object: Pointer to geometry to check
        """
    def SetEndPoint(self, endpoint: Point2D):
        """Set end (last) point of the path

        Args:
            endpoint: E point

        Returns:
            none
        """
    def SetStartPoint(self, startpoint: Point2D):
        """Set start (first) point of the path

        Args:
            startpoint: Start point

        Returns:
            none
        """
    def __eq__(self, path: Path2D) -> object:
        """Comparison of paths without tolerance.

        Be careful, this method work without tolerance!

        Args:
            path:Compared path.

        Returns:
            True when paths are equal, otherwise false.
        """
    @typing.overload
    def __iadd__(self, element: Path2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended

        Returns:
            Reference to path.
        """
    @typing.overload
    def __iadd__(self, element: Line2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Polyline2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Spline2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Clothoid2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Arc2D) -> Path2D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, path: Path2D):
        """Copy constructor

        Copy constructor is expensive because all data are cloned in new path.

        Args:
            path: Path which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndPoint(self) -> Point2D:
        """Get path end point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error
        """
    @EndPoint.setter
    def EndPoint(self, value: Point2D) -> None:
        """Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Set end (last) point of the path
        """
    @property
    def StartPoint(self) -> Point2D:
        """Get path start point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error
        """
    @StartPoint.setter
    def StartPoint(self, value: Point2D) -> None:
        """Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Set start (first) point of the path
        """

class Path2DList():
    """List for Path2D objects
    """
    def __contains__(self, value: Path2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Path2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Path2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Path2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Path2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Path2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Path2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Path3D(Path):
    """Representation class for 3D path.
    """
    @typing.overload
    def Add(self, element: Path3D) -> eGeometryErrorCode:
        """Add element into path Path3D

        Args:
            element: Path element to add

        Returns:
            error code
        """
    @typing.overload
    def Add(self, element_object: object) -> eGeometryErrorCode:
        """Add element into path Path3D

        Args:
            element_object: Pointer to element to add

        Returns:
            error code
        """
    def Add(self):
        """ Overloaded function. See individual overloads.
        """
    def DefinitionPoints(self) -> Polyline3D:
        """Extracts all definition points of the path.

        Returns:
            All definition points ( join points of sub curves in this path ) of this path as Polyline3D
        """
    def FirstDefinitionPoint(self) -> Point3D:
        """Extracts the first definition point of the path.

        Returns:
            First definition point of this path as Point3D
        """
    def GetEndPoint(self) -> Point3D:
        """Get path end point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Returns:
            const Point3D     End point
        """
    def GetEndRelPoint(self) -> Point3D:
        """Get relative end (last) point of the path

        Returns:
            End point (relative)
        """
    def GetStartPoint(self) -> Point3D:
        """Get path start point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Returns:
            const Point3D     Start point
        """
    def GetStartRelPoint(self) -> Point3D:
        """Get relative start (first) point of the path

        Returns:
            Start point (relative)
        """
    def IsClosed(self) -> bool:
        """Check for closed path, it mean that first point is same as last point

        Returns:
            True when path is closed, otherwise false.
        """
    @typing.overload
    def IsItPossibleToAddElement(self, pGeometry_object: object) -> bool:
        """Check if the geometry can be added into path Path3D

        Args:
            pGeometry_object: Pointer to geometry to check
        """
    @typing.overload
    def IsItPossibleToAddElement(self, pGeometry_object: object, tolerance: float) -> bool:
        """Check if the geometry can be added into path Path3D (with possible noncontinuous)

        Args:
            pGeometry_object: Geometries (are modified in case of non continuos geometries!)
            tolerance:        Tolerance for non continuous geometries

        Returns:
            Yes / no
        """
    def IsItPossibleToAddElement(self):
        """ Overloaded function. See individual overloads.
        """
    def IsValid(self) -> bool:
        """Validity check

        \warning Path doesn't have to be closed to be valid, you have to check this extra
        """
    @staticmethod
    def IsValidCurveType(pGeometry_object: object) -> bool:
        """Check if the geometry is supported by Path3D

        Args:
            pGeometry_object: Pointer to geometry to check
        """
    def SetEndPoint(self, endpoint: Point3D):
        """Set end (last) point of the path

        Args:
            endpoint: E point

        Returns:
            none
        """
    def SetStartPoint(self, startpoint: Point3D):
        """Set start (first) point of the path

        Args:
            startpoint: Start point

        Returns:
            none
        """
    def __eq__(self, path: Path3D) -> object:
        """Comparison of paths without tolerance.

        Be careful, this method work without tolerance!

        Args:
            path:Compared path.

        Returns:
            True when paths are equal, otherwise false.
        """
    @typing.overload
    def __iadd__(self, element: Path3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended

        Returns:
            Reference to path.
        """
    @typing.overload
    def __iadd__(self, element: Line3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Polyline3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Arc3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: Spline3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    @typing.overload
    def __iadd__(self, element: BSpline3D) -> Path3D:
        """Append operator

        Args:
            element: Element which will be appended
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, path: Path3D):
        """Copy constructor

        Copy constructor is expensive because all data are cloned in new path.

        Args:
            path: Path which will be copied.
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D):
        """Constructor defines a polyline of 2 points as path.

        Args:
            point1: First point of the polyline path
            point2: Second point of the polyline path
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D, point3: Point3D):
        """Constructor defines a polyline of 3 points as path.

        Args:
            point1: 1. point of the polyline path
            point2: 2. point of the polyline path
            point3: 3. point of the polyline path
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D, point3: Point3D, point4: Point3D):
        """Constructor defines a polyline of 4 points as path.

        Args:
            point1: 1. point of the polyline path
            point2: 2. point of the polyline path
            point3: 3. point of the polyline path
            point4: 4. point of the polyline path
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D, point3: Point3D, point4: Point3D, point5: Point3D):
        """Constructor defines a polyline of 5 points as path.

        Args:
            point1: 1. point of the polyline path
            point2: 2. point of the polyline path
            point3: 3. point of the polyline path
            point4: 4. point of the polyline path
            point5: 5. point of the polyline path
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndPoint(self) -> Point3D:
        """Get path end point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error
        """
    @EndPoint.setter
    def EndPoint(self, value: Point3D) -> None:
        """Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Set end (last) point of the path
        """
    @property
    def StartPoint(self) -> Point3D:
        """Get path start point

        Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error
        """
    @StartPoint.setter
    def StartPoint(self, value: Point3D) -> None:
        """Throw  THROW_GEO_EXCEPTION_OUT_OF_RANGE_ if path is empty
        Throw  THROW_GEO_EXCEPTION_GENERAL_ERROR_ if internal error

        Set start (first) point of the path
        """

class Path3DList():
    """List for Path3D objects
    """
    def __contains__(self, value: Path3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Path3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Path3DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Path3D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Path3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Path3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Path3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class PathIterator():
    """Path iterator
    """
    def __next__(self) -> object:
        """Get the next element
        """

class PerpendicularCalculus():
    """Class for perpendicular calculation
    """
    @staticmethod
    @typing.overload
    def Calculate(geoObject_object: object, inputPnt: Point3D, eps: float, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool,
                  Point3D, Vector2D]:
        """Calculates perpendicular point on IGeometry object.

        Args:
            geoObject_object: IGeometry on which to calculate perpendicular point
            inputPnt:         Projection point
            eps:              Tolerance for the perpendicular point calculation
            insideTolerance:  Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(path: Path2D, inputPnt: Point3D, eps: float, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D,
                  Vector2D]:
        """Calculates perpendicular point on a path of multiple objects.

        This calculation only delivers perpendicular point which are on the element

        Args:
            path:            Path on which to calculate perpendicular point
            inputPnt:        Projection point
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(path: Path2D, inputPnt: Point3D, eps: float, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D]:
        """Calculates perpendicular point on a path of multiple objects.

        This calculation only delivers perpendicular point which are on the element

        Args:
            path:            Path on which to calculate perpendicular point
            inputPnt:        Projection point
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point)
        """
    @staticmethod
    @typing.overload
    def Calculate(line2d: Line2D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Line2D object.

        Args:
            line2d:          Line2D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(line2d: Line2D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D]:
        """Calculates perpendicular point on Line2D object.

        Args:
            line2d:          Line2D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point)
        """
    @staticmethod
    @typing.overload
    def Calculate(axis: Axis2D, inputPnt: Point3D) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Axis2D object.

        This calculation only delivers perpendicular point which are on the element

        Args:
            axis:     Axis2D on which to calculate perpendicular point
            inputPnt: Projection point

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(line3d: Line3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D]:
        """Calculates perpendicular point on Line3D object.

        Args:
            line3d:          Line3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point)
        """
    @staticmethod
    @typing.overload
    def Calculate(line3d: Line3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Line3D object.

        Args:
            line3d:          Line3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline3d: Polyline3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D,
                  Vector2D]:
        """Calculates perpendicular point on Polyline3D object.

        Args:
            polyline3d:      Polyline3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(polygon3d: Polygon3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D,
                  Vector2D]:
        """Calculates perpendicular point on Polygon3D object.

        Args:
            polygon3d:       Polygon3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(polyhedron3d: Polyhedron3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D,
                  Vector2D]:
        """Calculates perpendicular point on Polyhedron3D object.

        Args:
            polyhedron3d:    Polyhedron3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(axis: Axis3D, inputPnt: Point3D) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Axis3D object.

        This calculation only delivers perpendicular point which are on the element

        Args:
            axis:     Axis3D on which to calculate perpendicular point
            inputPnt: Projection point

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc2D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Arc2D object.

        Args:
            arc:             Arc2D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline: Polyline2D, inputPnt: Point3D, subelement: int, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool,
                  Point3D, Vector2D]:
        """Calculates perpendicular point on Polyline2D object.

        This calculation only delivers perpendicular point which are on the element

        Args:
            polyline:        Polyline2D on which to calculate perpendicular point
            inputPnt:        Projection point
            subelement:      Line segment for calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: Spline2D, inputPnt: Point3D, eps: float) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Spline2D object.

        This calculation only delivers perpendicular point which are on the element

        Args:
            spline:   Spline2D on which to calculate perpendicular point
            inputPnt: Projection point
            eps:      Tolerance for the perpendicular point calculation

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(clothoid2D: Clothoid2D, inputPnt: Point3D, eps: float, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool,
                  Point3D, Vector2D]:
        """Calculates perpendicular point on Clothoid2D object.

        Args:
            clothoid2D:      Clothoid2D on which to calculate perpendicular point
            inputPnt:        Projection point
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(polygon2D: Polygon2D, inputPnt: Point3D) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Polygon2D object.

        This calculation only delivers perpendicular point which are on the element

        Args:
            polygon2D: Polygon2D on which to calculate perpendicular point
            inputPnt:  Projection point

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(vector2D: Vector2D, bPerpendicularLeft: bool) -> Vector2D:
        """Calculate perpendicular to given 2D vector

        Args:
            vector2D:           2D Vector on which to calculate perpendicular point
            bPerpendicularLeft: orientation of perpendicular vector, if true then to the left, if false then to the right

        Returns:
            Tangent of the perpendicular
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc3D, inputPnt: Point3D, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool, Point3D, Vector2D]:
        """Calculates perpendicular point on Arc3D object.

        Args:
            arc:             Arc3D on which to calculate perpendicular point
            inputPnt:        Projection point
            insideTolerance: Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point,
                  Tangent of the perpendicular)
        """
    @staticmethod
    @typing.overload
    def Calculate(geoObject_object: object, inputPnt: Point3D, eps: float, insideTolerance: float = 1.7976931348623157e+308) -> tuple[bool,
                  Point3D]:
        """Calculates perpendicular point on IGeometry object.

        Args:
            geoObject_object: IGeometry on which to calculate perpendicular point
            inputPnt:         Projection point
            eps:              Tolerance for the perpendicular point calculation
            insideTolerance:  Tolerance for the IsInsideElement(..) comparison

        Returns:
            tuple(True if perpendicular point calculation was successful,
                  Perpendicular point)
        """
    def Calculate(self):
        """ Overloaded function. See individual overloads.
        """
    def GetTangent(self) -> Vector2D:
        """Get the tangent of the geometry

        Returns:
            Tangent of the geometry
        """
    @staticmethod
    def IsInsideElement(geoElement_object: object, perPnt: Point3D, insideTolerance: float) -> bool:
        """Check, whether the perpendicular point is inside the element

        Args:
            geoElement_object: Geometry element
            perPnt:            Perpendicular point
            insideTolerance:   Allowed deviance to the end point outside the element

        Returns:
            Perpendicular point is inside the element: true/false
        """
    def IsSuccessful(self) -> bool:
        """Get the result of the calculation

        Returns:
            true if calculation successful, else false
        """
    @staticmethod
    def IsSupportedGeometry(geoObject_object: object) -> bool:
        """Check, whether geometry is supported

        Args:
            geoObject_object: Geometry element

        Returns:
            is supported
        """
    @typing.overload
    def __init__(self, path: Path2D, eps: float, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            path:            Path of concatenated IGeometry objects
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    @typing.overload
    def __init__(self, line: Line2D, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            line:            Line which will be held in a 2D path
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    @typing.overload
    def __init__(self, polyline: Polyline2D, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            polyline:        Polyline which will be held in a 2D path
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    @typing.overload
    def __init__(self, arc: Arc2D, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            arc:             Arc which will be held in a 2D path
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    @typing.overload
    def __init__(self, clothoid: Clothoid2D, eps: float, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            clothoid:        Clothoid which will be held in a 2D path
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    @typing.overload
    def __init__(self, spline: Spline2D, eps: float):
        """Constructor.

        This calculation only delivers perpendicular point which are on the element

        Args:
            spline: Spline which will be held in a 2D path
            eps:    Tolerance for the perpendicular point calculation
        """
    @typing.overload
    def __init__(self, polygon2D: Polygon2D):
        """Constructor.

        Args:
            polygon2D: Polygon which will be held in a 2D path
        """
    @typing.overload
    def __init__(self, element: PerpendicularCalculus):
        """Copy constructor

        Args:
            element: Element to copy
        """
    @typing.overload
    def __init__(self, geoObject: object, eps: float, insideTolerance: float = 1.7976931348623157e+308):
        """Constructor.

        Args:
            geoObject:       Geometry which will be held in a 2D path
            eps:             Tolerance for the perpendicular point calculation
            insideTolerance: Tolerance for the IsInsideElement(..) comparison
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """

class Plane3D():
    """Representation class for 3D plane.
    """
    def CalcPlaneVectors(self) -> tuple[Vector3D, Vector3D]:
        """Calc X and Y axis vectors for plane

        Returns:
            tuple(Vector of X axis,
                  Vector of Y axis)
        """
    def GetPoint(self) -> Point3D:
        """Get 3D Plane reference point

        Returns:
            Point3D.
        """
    def GetTransformationMatrix(self) -> Matrix3D:
        """Get transformation matrix for given plane 3D

        Returns:
            Matrix3D const reference
        """
    def GetVector(self) -> Vector3D:
        """Get the Normal Vector

        Returns:
            Vector3D.
        """
    def Set(self, point: Point3D, normalVector: Vector3D):
        """Initialize Plane from point and vector

        Args:
            point:        New point.
            normalVector: New vector.
        """
    def SetPoint(self, point: Point3D):
        """Set reference point

        Args:
            point: New point.
        """
    def SetVector(self, vec: Vector3D):
        """Set the Normal Vector

        Args:
            vec: New vector.
        """
    def __eq__(self, plane: Plane3D) -> object:
        """Comparison of planes without tolerance.

        Be careful, this method work without tolerance!

        Args:
            plane:Compared plane.

        Returns:
            True when planes are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, plane: Plane3D):
        """Copy constructor

        Args:
            plane: Plane which will be copied.
        """
    @typing.overload
    def __init__(self, point: Point3D, normalVector: Vector3D):
        """Constructor

        Create 3D Plane with given point and vector

        Args:
            point:        Init point of the plane.
            normalVector: Init vector of the plane.
        """
    @typing.overload
    def __init__(self, point1: Point3D, point2: Point3D, point3: Point3D):
        """Constructor

        Create 3D Plane from three points which lies on this plane.
        If plane can not be computed, then constructor throw geometry exception 'Incorrect parameters'.

        Args:
            point1: 1st point on the plane.
            point2: 2nd point on the plane.
            point3: 3rd point on the plane.
        """
    @typing.overload
    def __init__(self, axis: Axis3D):
        """Create a plane from a 3D axis

        Args:
            axis: Axis
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> Plane3D:
        """2D matrix transformation.

        Args:
            matrix: 2D transformation Matrix

        Returns:
            Copy of transformed 3D plane.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix3D) -> Plane3D:
        """3D matrix transformation.

        Args:
            matrix: 3D transformation Matrix

        Returns:
            Copy of transformed 3D plane.
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Point(self) -> Point3D:
        """Get 3D Plane reference point
        """
    @Point.setter
    def Point(self, value: Point3D) -> None:
        """Set reference point
        """
    @property
    def Vector(self) -> Vector3D:
        """Get the Normal Vector
        """
    @Vector.setter
    def Vector(self, value: Vector3D) -> None:
        """Set the Normal Vector
        """

class Point2D():
    """Representation class for 2D point
    """
    def GetCoords(self) -> tuple[float, float]:
        """Get copy of X,Y coordinates.

        Returns:
            tuple(X coordinate of point,
                  Y coordinate of point)
        """
    def GetDistance(self, point: Point2D) -> float:
        """Get distance.

        Formula: Result(double) = |A-B|.

        Args:
            point: Point2D.

        Returns:
            double.
        """
    def IsZero(self) -> bool:
        """Check the coords [0.0,0.0].

        If the coords are zero, the return value is true.
        If the coords aren't zero, the return value is false.

        Returns:
            bool.
        """
    @typing.overload
    def Set(self, point: Point2D):
        """Set the coordinate.

        Args:
            point: Point.
        """
    @typing.overload
    def Set(self, x: float, y: float):
        """Initialize from x,y coordinates.

        Args:
            x: coordinate.
            y: coordinate.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def SetX(self, x: float):
        """Set the coordinate.

        Args:
            x: coordinate.
        """
    def SetY(self, y: float):
        """Set the coordinate.

        Args:
            y: coordinate.
        """
    def Values(self) -> list[float]:
        """Get copy of X,Y coordinates as python list.

        Returns:
            X coordinate of point.,
            Y coordinate of point.
        """
    @typing.overload
    def __add__(self, point: Point2D) -> Point2D:
        """Point translation by point.

         Formula: Point(new) = Point(this) + Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector2D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    @typing.overload
    def __add__(self, vec: Vector2D) -> Point2D:
        """Move the point by vector

        Args:
            vec: Vector

        Returns:
            New point
        """
    def __add__(self, dummy: typing.Any):
        """ Overloaded function. See individual overloads.

        Args:
            dummy:  dummy parameter

        Returns:
            dummy
        """
    def __eq__(self, point: Point2D) -> bool:
        """Comparison of points without tolerance.

        Be careful, this method work without tolerance!

        Args:
            point: Compared point.

        Returns:
            True when points are equal, otherwise false.
        """
    def __iadd__(self, point: Point2D) -> Point2D:
        """Point translation by point.

        Formula: Point(this) = Point(this) + Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector2D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    def __idiv__(self, divider: float) -> Point2D:
        """Divide operator.

        Formula:
             Point(this).X = Point(this).X / divider
             Point(this).Y = Point(this).Y / divider

        This method is checked and throwing Geometry::Exception when divider is zero.

        Args:
            divider: Divider.

        Returns:
            Point.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, point: Point2D):
        """Copy constructor.

        Args:
            point: Point which will be copied.
        """
    @typing.overload
    def __init__(self, point: Point3D):
        """Explicit copy constructor.

        Copy only X_COORD and Y_COORD from point

        Args:
            point: 3D Point which will be copied to the 2D point.
        """
    @typing.overload
    def __init__(self, refPoint: Point2D, point: Point2D):
        """Constructor.

        Initialize point from point in local coordinate system.
        Formula: Result = refPoint + point

        Args:
            refPoint: Reference point.
            point:    Relative point.
        """
    @typing.overload
    def __init__(self, x: float, y: float):
        """Constructor.

        Initialize point from single coordinates in world coordinate system.

        Args:
            x: X coordinate of point.
            y: Y coordinate of point.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, point: Point2D) -> Point2D:
        """Point translation by negative point

         Formula: Point(this) = Point(this) - Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector2D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    def __mul__(self, matrix: Matrix2D) -> Point2D:
        """Matrix transformation.

        Result = Point * matrix

        Args:
            matrix: Transformation Matrix.

        Returns:
            Point.
        """
    def __ne__(self, point: Point2D) -> bool:
        """Comparison of points without tolerance.

        Be careful, this method works without tolerance!

        Args:
            point: Compared point.

        Returns:
            True when points are not equal, otherwise false.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @typing.overload
    def __sub__(self, vec: Vector2D) -> Point2D:
        """Move the point by reversed vector

        Args:
            vec: Vector

        Returns:
            New point
        """
    @typing.overload
    def __sub__(self, point: Point2D) -> Point2D:
        """Point translation by negative point

         Formula: Point(new) = Point(this) - Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector2D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    def __sub__(self):
        """ Overloaded function. See individual overloads.
        """
    def __truediv__(self, divider: float) -> Point2D:
        """Divide operator.

        Formula:
             Point(new).X = Point(this).X / divider
             Point(new).Y = Point(this).Y / divider

        Args:
            divider: Divider.

        Returns:
            Point.
        """
    @property
    def To3D(self) -> Point3D:
        """convert to 3D3
        """
    @To3D.setter
    def To3D(self, value: Point3D) -> None:
        """convert to 3D3
        """
    @property
    def X(self) -> float:
        """Get the x coordinate.
        """
    @X.setter
    def X(self, x: float) -> None:
        """Set the coordinate.

        Args:
            x: coordinate.
        """
    @property
    def Y(self) -> float:
        """Get the y coordinate.
        """
    @Y.setter
    def Y(self, y: float) -> None:
        """Set the coordinate.

        Args:
            y: coordinate.
        """

class Point2DList():
    """List for Point2D objects
    """
    def __contains__(self, value: Point2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Point2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Point2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Point2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Point2DList:
        """Add a list

        Args:
            eleList: Point2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Point2D):
        """Constructor with a Point2D

        Args:
            ele: Point2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Point2D

        Args:
            eleList: Point2D list
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
    def __setitem__(self, index: (int | slice), value: Point2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Point2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Point2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Point2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Point3D():
    """Representation class for 3D point
    """
    def GetCoords(self) -> tuple[float, float, float]:
        """Get copy of X,Y,Z coordinates

        Returns:
            tuple(X coordinate of point,
                  Y coordinate of point,
                  Z coordinate of point)
        """
    def GetDistance(self, point: Point3D) -> float:
        """Get distance

        Formula: Result(double) = |A-B|.

        Args:
            point: Point3D.

        Returns:
            double.
        """
    def IsZero(self) -> bool:
        """Check the coords [0.0, 0.0, 0.0]

        If the coords are zero, the return value is true.
        If the coords aren't zero, the return value is false.

        Returns:
            bool.
        """
    @typing.overload
    def Set(self, point: Point3D):
        """Initialize from point 3D.

        Args:
            point: Point.
        """
    @typing.overload
    def Set(self, x: float, y: float, z: float):
        """Initialize from x,y,z coordinates.

        Args:
            x: coordinate.
            y: coordinate.
            z: coordinate.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def Values(self) -> list[float]:
        """Get copy of X,Y,Z coordinates as python list

        Returns:
            X coordinate of point,
            Y coordinate of point,
            Z coordinate of point
        """
    @typing.overload
    def __add__(self, vec: Vector3D) -> Point3D:
        """Move the point by vector 3D

        Args:
            vec: Vector

        Returns:
            New point
        """
    @typing.overload
    def __add__(self, vec: Vector2D) -> Point3D:
        """Move the point by vector 2D. Z axis will be ignored

        Args:
            vec: Vector

        Returns:
            New point
        """
    @typing.overload
    def __add__(self, point: Point3D) -> Point3D:
        """Point translation by point

         Formula: Point(new) = Point(this) + Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector3D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    def __add__(self, dummy: typing.Any):
        """ Overloaded function. See individual overloads.

        Args:
            dummy:  dummy parameter

        Returns:
            dummy
        """
    def __eq__(self, point: Point3D) -> bool:
        """Comparison of points without tolerance.

        Be careful, this method work without tolerance!

        Args:
            point: Compared point.

        Returns:
            True when points are equal, otherwise false.
        """
    def __iadd__(self, point: Point3D) -> Point3D:
        """Point translation by point

         Formula: Point(this) = Point(this) + Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector3D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    def __idiv__(self, divider: float) -> Point3D:
        """Divide operator.

        Formula:
             Point(this).X = Point(this).X / divider
             Point(this).Y = Point(this).Y / divider
             Point(this).Z = Point(this).Z / divider

        This method is checked and throwing Geometry::Exception when divider is zero.

        Args:
            divider: Divider.

        Returns:
            Point.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, point: Point3D):
        """Copy constructor.

        Args:
            point: Point which will be copied.
        """
    @typing.overload
    def __init__(self, point: Point2D):
        """Explicit copy constructor.

        Copy only X_COORD and Y_COORD from point, Z_COORD is set to zero.

        Args:
            point: 2D Point which will be copied to the 3D point.
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, point: Point3D):
        """Constructor.

        Initialize point from point in local coordinate system.
        Formula: Result = refPoint + point

        Args:
            refPoint: Reference point.
            point:    Relative point
        """
    @typing.overload
    def __init__(self, x: float, y: float, z: float):
        """Constructor

        Initialize point from single coordinates in world coordinate system.

        Args:
            x: X coordinate of point
            y: Y coordinate of point
            z: Z coordinate of point
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, point: Point3D) -> Point3D:
        """Point translation by negative point

         Formula: Point(this) = Point(this) - Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector3D operand.

        Args:
            point: Point.

        Returns:
            Point.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> Point3D:
        """2D matrix transformation.

        Result = Point * matrix

        Args:
            matrix: 2D transformation Matrix

        Returns:
            Point.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix3D) -> Point3D:
        """3D matrix transformation.

        Result = Point * matrix

        Args:
            matrix: 3D transformation Matrix

        Returns:
            Point.
        """
    @typing.overload
    def __mul__(self, scale: float) -> Point3D:
        """Scale point with constant

        Result = Point * scale

        Args:
            scale: - scale factor

        Returns:
            scaled Point
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, point: Point3D) -> bool:
        """Comparison of points without tolerance.

        Be careful, this method work without tolerance!

        Args:
            point: Compared point.

        Returns:
            True when points are not equal, otherwise false.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @typing.overload
    def __sub__(self, vec: Vector3D) -> Point3D:
        """Move the point by reversed vector 3D

        Args:
            vec: 3D vector

        Returns:
            New point
        """
    @typing.overload
    def __sub__(self, vec: Vector2D) -> Point3D:
        """Move the point by reversed vector 2D. Z coordinate stays unchanged.

        Args:
            vec: 2D vector

        Returns:
            New point
        """
    @typing.overload
    def __sub__(self, point: Point3D) -> Point3D:
        """Point translation by negative point

         Formula: Point(new) = Point(this) - Point

        This is not standard math operation and is implemented only as practical use case
        for point moving in %Allplan. In this case given operand point represent
        offset from Zero point.
        For standard move operation please use Service::Move method with Vector3D operand.

        Args:
            point: Point3D.

        Returns:
            Point.
        """
    def __sub__(self):
        """ Overloaded function. See individual overloads.
        """
    def __truediv__(self, divider: float) -> Point3D:
        """Divide operator.

        Formula:
             Point(new).X = Point(this).X / divider
             Point(new).Y = Point(this).Y / divider
             Point(new).Z = Point(this).Z / divider

        Args:
            divider: Divider.

        Returns:
            Point.
        """
    @property
    def To2D(self) -> Point2D:
        """convert to 2D3
        """
    @To2D.setter
    def To2D(self, value: Point2D) -> None:
        """convert to 2D3
        """
    @property
    def X(self) -> float:
        """Get the x coordinate
        """
    @X.setter
    def X(self, value: float) -> None:
        """Set  the x coordinate
        """
    @property
    def Y(self) -> float:
        """Get the y coordinate
        """
    @Y.setter
    def Y(self, value: float) -> None:
        """Set  the y coordinate
        """
    @property
    def Z(self) -> float:
        """Get the z coordinate
        """
    @Z.setter
    def Z(self, value: float) -> None:
        """Set  the z coordinate
        """

class Point3DList():
    """List for Point3D objects
    """
    def __contains__(self, value: Point3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Point3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Point3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Point3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Point3DList:
        """Add a list

        Args:
            eleList: Point3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Point3D):
        """Constructor with a Point3D

        Args:
            ele: Point3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Point3D

        Args:
            eleList: Point3D list
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
    def __setitem__(self, index: (int | slice), value: Point3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Point3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Point3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Point3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class BSpline2D(PolyPoints2D):
    """class for 2D (non uniform, rational) B-spline geometry
    """
    def Clear(self):
        """Clear data, getting invalid state
        """
    @staticmethod
    def CreateLine2D(line: Line2D) -> BSpline2D:
        """Create BSpline2D from Line2D

        Args:
            line: Input line.

        Returns:
            Created BSpline2D.
        """
    def Get(self) -> tuple[list[Point2D], list[float], list[float], int, bool]:
        """Return type: tuple(list(Point2D), list(float), list(float), int, bool)
        """
    def GetDegree(self) -> int:
        """Gets spline degree

        Returns:
            spline degree
        """
    def GetKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get knot vector

        Returns:
            knot vector const reference
        """
    def GetWeights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights

        Returns:
            weights vector const reference
        """
    def IsClosed(self) -> bool:
        """Check if spline is closed ( first/last points are equal )

        Returns:
            closed spline true/false
        """
    def IsRational(self) -> bool:
        """Check if the spline is rational

        Returns:
            bool true = rational
        """
    def IsValid(self) -> bool:
        """Check spline validity

        Returns:
            bool valid = true
        """
    def Reverse(self):
        """Reverse of current spline

        Method reverse Spline using reverse from PolyPoints and swapping tangents.
        """
    def Set(self, points: Point2DList, weights: NemAll_Python_Utility.VecDoubleList, knots: NemAll_Python_Utility.VecDoubleList,
            degree: int, isPeriodic: bool):
        """Get/Set functions

        Args:
            points
            weights
            knots
            degree
            isPeriodic
        """
    def SetDegree(self, degree: int):
        """Set spline degree

        Args:
            degree: desired degree
        """
    def SetKnots(self, knots: NemAll_Python_Utility.VecDoubleList):
        """Set knot vector

        Args:
            knots: knot vector to set
        """
    def SetPeriodic(self, arg2: bool):
        """Set the periodic flag

        Args:
            flag:  True if BSpline is periodic
        """
    def SetWeights(self, weights: NemAll_Python_Utility.VecDoubleList):
        """Set weights for control points

        Args:
            weights: weights vector to set
        """
    def __eq__(self, bspline: BSpline2D) -> object:
        """Comparison of bsplines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            bspline:Compared bspline.

        Returns:
            True when bsplines are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, points: Point2DList, weights: NemAll_Python_Utility.VecDoubleList, knots: NemAll_Python_Utility.VecDoubleList,
                 degree: int, isPeriodic: bool):
        """Constructor from b-spline data.
        Creates b-spline using provided data.

        Args:
            points:     control points of b-spline.
            weights:    weights of b-spline.
            knots:      knots of b-spline.
            degree:     degree of b-spline.
            isPeriodic: flag of periodicity of b-spline.
        """
    @typing.overload
    def __init__(self, spline: BSpline2D):
        """Copy constructor.

        Args:
            spline: Spline which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Degree(self) -> int:
        """Gets spline degree
        """
    @Degree.setter
    def Degree(self, degree: int) -> None:
        """Gets spline degree

        Set spline degree

        Args:
            degree: desired degree
        """
    @property
    def IsPeriodic(self) -> bool:
        """Check if the spline is periodic
        """
    @IsPeriodic.setter
    def IsPeriodic(self, value: bool) -> None:
        """Check if the spline is periodic
        """
    @property
    def Knots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get knot vector
        """
    @Knots.setter
    def Knots(self, knots: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set knot vector

        Args:
            knots: knot vector to set
        """
    @property
    def Weights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights
        """
    @Weights.setter
    def Weights(self, weights: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set weights for control points

        Args:
            weights: weights vector to set
        """

class BSpline3D(PolyPoints3D):
    """class for 3D (non uniform, rational) B-spline geometry
    """
    def Clear(self):
        """Clear data, getting invalid state
        """
    @staticmethod
    def Create(curve: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D) -> BSpline3D:
        """Create BSpline from ICurve3D

        Args:
            curve: Input curve

        Returns:
            Created BSpline3D.
        """
    @staticmethod
    def CreateArc3D(arc: Arc3D) -> BSpline3D:
        """Create BSpline form Arc3D

        Args:
            arc: Input arc

        Returns:
            Created Bspline3D
        """
    @staticmethod
    def CreateBSpline(points: Point3DList, degree: int, isPeriodic: bool) -> BSpline3D:
        """Create BSpline from control points

        Args:
            points:     Control points
            degree:     Degree of BSpline
            isPeriodic: true if BSpline should be smoothly closed

        Returns:
            BSpline object
        """
    @staticmethod
    def CreateBSpline3DFrom2DCurves(directionCurve: object, elevationCurve: object, startHeight: float,
                                    chainPoints: Point3DList) -> tuple[eGeometryErrorCode, BSpline3D]:
        """Creates BSpline3D from direction 2D curve and elevation 2D curve

        Args:
            directionCurve: direction curve ( for X,Y coordinates)
            elevationCurve: elevation curve (for Z coordinates)
            startHeight:    Z coordinate of new curve start point
            chainPoints:    list of chain points to match resulting curve

        Returns:
            tuple(eOK if successful,
                  created BSpline3D)
        """
    @staticmethod
    def CreateBSpline3DFromAxisAndGradient(directionCurve: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D,
                                           elevationCurve: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D, startHeight: float, chainPoints: Point3DList) -> tuple:
        """Create BSpline3D curve from axis and gradient (all placed in XY plane)

        Args:
            directionCurve: direction/axis curve
            elevationCurve: elevation/gradient curve
            startHeight:    Z coordinate of new curve start point
            chainPoints:    list of chain points to match resulting curve

        Returns:
            tuple(error code,
                  result BSpline3D curve)
        """
    @staticmethod
    def CreateBSplineInterpolated(points: Point3DList, degree: int, isPeriodic: bool) -> BSpline3D:
        """Create BSpline from interpolated points

        Args:
            points:     Interpolated points
            degree:     Degree of BSpline
            isPeriodic: true if BSpline should be smoothly closed

        Returns:
            BSpline object
        """
    @staticmethod
    def CreateBSplineJoined(curves: Curve3DList) -> BSpline3D:
        """Create BSpline by joining curves. Curves should meet by end points.

        Args:
            curves: Source curves

        Returns:
            BSpline object (empty, if joining failed)
        """
    @staticmethod
    def CreateLine3D(line: Line3D) -> BSpline3D:
        """Create BSpline3D from Line3D

        Args:
            line: Input line.

        Returns:
            Created BSpline3D.
        """
    @staticmethod
    def CreatePolyline3D(polyline3d: Polyline3D) -> BSpline3D:
        """Create a BSpline out of a Polyline3D object

        Args:
            polyline3d: Polyline3D that will be used for conversion

        Returns:
            An instance of the created BSpline3D
        """
    @staticmethod
    def CreateSpline(spline: Spline3D) -> BSpline3D:
        """Create BSpline from Spline3D

        Args:
            spline: Spline

        Returns:
            Created BSpline3D.
        """
    def EvaluateEndPoint(self) -> tuple[eGeometryErrorCode, Point3D]:
        """Evaluate end point of bspline

        Returns:
            evaluated end point
        """
    def EvaluateEndRelPoint(self) -> tuple[eGeometryErrorCode, Point3D]:
        """Evaluate relative end (last) point of bspline

        Returns:
            evaluated relative end point
        """
    def EvaluatePoint(self, param: float) -> tuple[eGeometryErrorCode, Point3D]:
        """Evaluate point of b-spline

        Args:
            param: parameter to evaluate point on b-spline

        Returns:
            tuple(error code of evaluation,
                  resulting point, if succeeded)
        """
    def EvaluatePointsWithTangents(self, parameters: NemAll_Python_Utility.VecDoubleList) -> list[tuple[Point3D, Vector3D]]:
        """Evaluate points and tangents of b-spline

        Args:
            parameters: parameters to evaluate points and tangents on b-spline

        Returns:
            vector of resulting points and tangents, if calculation failed for any parameter, empty vector is returned
        """
    def EvaluateStartPoint(self) -> tuple[eGeometryErrorCode, Point3D]:
        """Evaluate start point of bspline

        Returns:
            evaluated start point
        """
    def EvaluateStartRelPoint(self) -> tuple[eGeometryErrorCode, Point3D]:
        """Evaluate relative start point of bspline

        Returns:
            evaluated relative start point
        """
    def Get(self) -> tuple[Point3DList, NemAll_Python_Utility.VecDoubleList, NemAll_Python_Utility.VecDoubleList, int, bool]:
        """Return type: tuple( Point3DList, VecDoubleList, VecDoubleList, int, bool)
        """
    def GetDegree(self) -> int:
        """Gets spline degree

        Returns:
            spline degree
        """
    def GetInterpolatedPoints(self) -> Point3DList:
        """Function returns interpolated points of b-spline

        Returns:
            list of interpolated points
        """
    def GetInterpolatedPointsParameters(self) -> NemAll_Python_Utility.VecDoubleList:
        """Function returns list of parameters for interpolated points of b-spline

        Returns:
            list of parameters of interpolated points
        """
    def GetInterval(self) -> tuple[bool, float, float]:
        """Function returns the interval of bspline

        Returns:
            tuple(true if success,
                  start of curve interval,
                  end of curve interval)
        """
    def GetKnotMultiplicities(self) -> tuple[NemAll_Python_Utility.VecDoubleList, NemAll_Python_Utility.VecSizeTList]:
        """Get knot vector and knot multiplicities

        Returns:
            tuple(knot vector with unique values,
                  knot multiplicities)
        """
    def GetKnots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get knot vector

        Returns:
            knot vector
        """
    def GetParametersForDistances(self, distances: NemAll_Python_Utility.VecDoubleList) -> NemAll_Python_Utility.VecDoubleList:
        """Find parameters for distances on b-spline

        Args:
            distances: list of distances to calculate parameters for

        Returns:
            list of parameters, if calculation failed for any distance, empty vector is returned
        """
    def GetWeights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights

        Returns:
            weights vector
        """
    def IsClosed(self) -> bool:
        """Check if spline is closed ( first/last points are equal )

        Returns:
            closed spline true/false
        """
    def IsEndClamped(self) -> bool:
        """Function returns whether the bspline is clamped at the end

        Returns:
            true if clamped on end
        """
    def IsLine(self) -> bool:
        """Check if bspline is line

        Returns:
            Returns true if it is line
        """
    def IsPeriodicClosed(self) -> bool:
        """Returns whether the spline is periodic or closed in 1st degree

        BSpline with degree == 1 cannot be periodic, wherefore returns true if closed.

        Returns:
            bool true = periodic or closed
        """
    def IsRational(self) -> bool:
        """Check if the spline is rational

        Returns:
            bool true = rational
        """
    def IsStartClamped(self) -> bool:
        """Function returns whether the bspline is clamped at the start

        Returns:
            true if clamped on start
        """
    def IsValid(self) -> bool:
        """Check spline validity

        Returns:
            bool valid = true
        """
    def Reverse(self):
        """Reverse of current spline

        Method reverse Spline using reverse from PolyPoints and swapping tangents.
        """
    def Set(self, points: Point3DList, weights: NemAll_Python_Utility.VecDoubleList, knots: NemAll_Python_Utility.VecDoubleList,
            degree: int, isPeriodic: bool = False):
        """Args:
            points
            weights
            knots
            degree
            isPeriodic
        """
    def SetDegree(self, degree: int):
        """Set spline degree

        Args:
            degree: desired degree
        """
    def SetKnots(self, knots: NemAll_Python_Utility.VecDoubleList):
        """Set knot vector

        Args:
            knots: knot vector to set
        """
    def SetPeriodic(self, periodic: bool):
        """Set periodic flag

        Args:
            periodic: value of periodic flag
        """
    def SetWeights(self, weights: NemAll_Python_Utility.VecDoubleList):
        """Set weights for control points

        Args:
            weights: weights vector to set
        """
    def __eq__(self, bspline: BSpline3D) -> object:
        """Comparison of bsplines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            bspline:Compared bspline.

        Returns:
            True when bsplines are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, points: Point3DList, weights: NemAll_Python_Utility.VecDoubleList, knots: NemAll_Python_Utility.VecDoubleList,
                 degree: int, isPeriodic: bool = False):
        """Default constructor.
        Creates invalid spline.

        Args:
            points
            weights
            knots
            degree
            isPeriodic
        """
    @typing.overload
    def __init__(self, spline: BSpline3D):
        """Copy constructor.

        Args:
            spline: Spline which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def Degree(self) -> int:
        """Gets spline degree
        """
    @Degree.setter
    def Degree(self, degree: int) -> None:
        """Gets spline degree

        Set spline degree

        Args:
            degree: desired degree
        """
    @property
    def IsPeriodic(self) -> bool:
        """Returns whether the spline is periodic

        Returns only given flag which was originally set
        """
    @IsPeriodic.setter
    def IsPeriodic(self, periodic: bool) -> None:
        """Returns whether the spline is periodic

        Returns only given flag which was originally set

        Set periodic flag

        Args:
            periodic: value of periodic flag
        """
    @property
    def Knots(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get knot vector
        """
    @Knots.setter
    def Knots(self, knots: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set knot vector

        Args:
            knots: knot vector to set
        """
    @property
    def Weights(self) -> NemAll_Python_Utility.VecDoubleList:
        """Get control points weights
        """
    @Weights.setter
    def Weights(self, weights: NemAll_Python_Utility.VecDoubleList) -> None:
        """Set weights for control points

        Args:
            weights: weights vector to set
        """

class Polygon2D(PolyPoints2D):
    """Representation of a two dimensional polygon

    To construct a valid polygon from a bunch of points, the following rules must be fulfilled:

    -   First and last point must coincide. This class does not 'auto-close' polygons! A quadratic shape
        with '4' edges has to be defined by passing 5 points to a constructor. For such an object, the Count()
        method will return 5 accordingly.
    -   The orientation of the points must be monotonous. It can be either clockwise or counter-clockwise.
    -   The polygon must not self-intersect itself. You can create polygons that self-intersect or have alternating
        orientation, but in those cases some methods will raise errors or return wrong calculation results.

    Each polygon consists of one or more _components_. A _component_ is a closed loop, representing either a solid
    or a cut-out, depending on the orientation of the loop (if counter-clockwise is solid element, then clockwise is
    a cut-out). Each component must be closed (first and last point coincide).

    """
    @staticmethod
    def CreateRectangle(leftBottom: Point2D, rightTop: Point2D) -> Polygon2D:
        """Create a rectangle

        Args:
            leftBottom: Left bottom point
            rightTop:   Right top point

        Returns:
            Polygon of the rectangle
        """
    def GetSegments(self) -> tuple[eGeometryErrorCode, list[Line2D]]:
        """Get polygon segments

        Returns:
            tuple(error code,
                  vector of polygon segments)
        """
    def IsValid(self) -> bool:
        """Check if the polygon is valid ( has at least 3 points )

        For additional point validation use Service::Validate.

        Returns:
            true if is valid
        """
    def Normalize(self, normalizeType: ePolygonNormalizeType = ePolygonNormalizeType.DEFAULT_NORM_TYPE, extra_smooth: bool = False):
        """Normalize Polygon2D.

        Using huge old algorithm, adding points at line crossings, reorganizing the lines, correcting gaps, ...
        This method is checked and throwing Exception when error occurs.

        Args:
            normalizeType: type of Polygon2D normalization
            extra_smooth:  Including extra smooth: true/false
        """
    def NormalizeNoThrow(self, normalizeType: ePolygonNormalizeType = ePolygonNormalizeType.DEFAULT_NORM_TYPE,
                         extra_smooth: bool = False) -> eGeometryErrorCode:
        """Normalize Polygon2D.

        Same as Normalize, but method doesn't throw exception, just return error code

        Args:
            normalizeType: type of Polygon2D normalization
            extra_smooth:  Including extra smooth: true/false

        Returns:
            Error code (eOK, eAllocError, eStructuralError)
        """
    def Reverse(self):
        """Reverse the point order in polygon, separatelly for every subpolygon
        """
    def __eq__(self, polygon2: Polygon2D) -> bool:
        """Equal operator

        Args:
            polygon2: Second polygon

        Returns:
            Polyline3D are equal
        """
    def __iadd__(self, point: Point2D) -> Polygon2D:
        """Addition assignment operator

        Args:
            point: Point which will be added

        Returns:
            Reference to polygon
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, pntList: list):
        """Constructor with an initializer list

        Args:
            pntList: Point list
        """
    @typing.overload
    def __init__(self, polygon: Polygon2D):
        """Copy constructor.

        Args:
            polygon: Polygon which will be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, polygon2: Polygon2D) -> bool:
        """Not equal operator

        Args:
            polygon2: Second polygon

        Returns:
            Polyline3D are equal
        """
    def __repr__(self) -> str:
        """Convert to string
        """

class Polygon2DList():
    """List for Polygon2D objects
    """
    def __contains__(self, value: Polygon2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Polygon2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Polygon2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Polygon2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Polygon2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Polygon2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Polygon2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Polygon2DUtil():

    @staticmethod
    def CalculateInscribedCircumscribedArc(outline: Polygon2D, centerPoint: Point2D, isCircumscribed: bool) -> tuple[Arc2D, Arc2D]:
        """Create the inscribed/ circumscribed arc for a regular polygon

        Args:
            outline:         Regular polygon
            centerPoint:     Center point of the regular polygon
            isCircumscribed: True, if

        Returns:
            tuple(Circumscribing arc of the regular polygon,
                  Inscribing arc of the regular polygon)
        """
    @staticmethod
    def CreateRegularPolygonFromArc(arc: Arc2D, placement: AxisPlacement2D, segmentation: int, bInscribed: bool) -> tuple[bool, Polygon2D]:
        """Create a regular polygon for an arc

        Args:
            arc:          Base arc
            placement:    Placement for the poylgon
            segmentation: Number of corner points
            bInscribed:   True, if if the arc is inscribed to the polygon

        Returns:
            tuple(true, if the polygonization was correct,
                  Regular polygon)
        """
    @staticmethod
    def FindPointOnPolygonWithDistance(polygon: Polygon2D, fromPoint: Point2D, directionPoint: Point2D, iAxisCurve_object: object,
                                       pointDistance: float) -> tuple[int, Point2D]:
        """Find a point on a polygon with a distance

        Args:
            polygon:           Polygon
            fromPoint:         From point
            directionPoint:    Direction point
            iAxisCurve_object: Axis curve
            pointDistance:     Point distance

        Returns:
            Found state, Distance point
        """
    @staticmethod
    def GetPolygon2DSegment(polygon: Polygon2D, clickPoint: Point2D) -> tuple[int, int, Line2D]:
        """Get the closest segment for the given click point

        Args:
            polygon:    Polygon to analyze
            clickPoint: Click point to analyze

        Returns:
            tuple(Index of the start point of the clicked line,
                  Index of the end point of the clicked line,
                  Segment of the polygon, where the click point is on)
        """

class Polygon3D(PolyPoints3D):
    """Representation of a plane polygon in a three dimensional space

    To construct a valid 3D polygon from a bunch of points, the following rules must be fulfilled:

    -   First and last point must coincide. This class does not 'auto-close' polygons! A quadratic shape
        with '4' edges has to be defined by passing 5 points to a constructor. For such an object, the Count()
        method will return 5 accordingly.
    -   The orientation of the points must be monotonous. It can be either clockwise or counter-clockwise.
    -   All the points must be coplanar.
    -   The polygon must not self-intersect itself. You can create polygons that self-intersect or have alternating
        orientation, but in those cases some methods will raise errors or return wrong calculation results.

    Each polygon consists of one or more _components_. A _component_ is a closed loop, representing either a solid
    or a cut-out, depending on the orientation of the loop (if counter-clockwise is solid element, then clockwise is
    a cut-out). Each component must be closed (first and last point coincide).
    """
    def GetLines(self) -> Line3DList:
        """Get edge lines of polygon

        Returns:
            Edge lines of polygon
        """
    def GetPlane(self) -> tuple[eGeometryErrorCode, Plane3D]:
        """Calculate plane

        Returns:
            Plane where polygon is
        """
    def GetVertices(self) -> object:
        """Get polygon vertices

        Returns:
            polygon vertices
        """
    def InsertPolygon(self, polygon: Polygon3D, position: int = -1) -> bool:
        """Insert a polygon into current one

        Args:
            polygon:  Polygon which will be inserted
            position: Position where the polygon will be inserted

        Returns:
            true if insert was successful
        """
    def IsValid(self) -> bool:
        """Check polygon validity

        Returns:
            true = valid, false = not valid
        """
    def IsValidStatus(self) -> tuple:
        """Check polygon validity

        Returns:
            true = valid, false = not valid,
            If polygon is invalid, here is the reason.
        """
    def Normalize(self, normalizeType: ePolygonNormalizeType = ePolygonNormalizeType.DEFAULT_NORM_TYPE, extra_smooth: bool = False):
        """Normalization of 3d polygon

        Args:
            normalizeType: Normalization type
            extra_smooth:  Increase level of details
        """
    def NormalizeNoThrow(self, normalizeType: ePolygonNormalizeType = ePolygonNormalizeType.DEFAULT_NORM_TYPE,
                         extra_smooth: bool = False) -> eGeometryErrorCode:
        """Normalize Polygon3D.

        Same as Normalize, but method doesn't throw exception, just return error code

        Args:
            normalizeType: type of Polygon2D normalization
            extra_smooth:  Including extra smooth: true/false

        Returns:
            Error code (eOK, eAllocError, eStructuralError, eWrongShape)
        """
    def Reverse(self):
        """Reverse the point order in polygon, separately for every sub-polygon
        """
    def __eq__(self, polygon2: Polygon3D) -> bool:
        """Equal operator

        Args:
            polygon2: Second polygon

        Returns:
            Polyline3D are equal
        """
    @typing.overload
    def __iadd__(self, polygon: Polygon3D) -> Polygon3D:
        """Addition assignment operator

        Args:
            polygon: Polygon which will be copied

        Returns:
            Reference to polygon
        """
    @typing.overload
    def __iadd__(self, point: Point3D) -> Polygon3D:
        """Addition assignment operator

        Args:
            point: New Point3D which will be added to the polygon

        Returns:
            Reference to polygon
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, pntList: list[Point3D]):
        """Constructor with an initializer list

        Args:
            pntList: Point list
        """
    @typing.overload
    def __init__(self, polygon: Polygon3D):
        """Copy constructor.

        Args:
            polygon: Polygon which will be copied
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix3D) -> Polygon3D:
        """Matrix transformation

        Args:
            matrix: Transformation matrix

        Returns:
            Reference to polygon
        """
    def __ne__(self, polygon2: Polygon3D) -> bool:
        """Not equal operator

        Args:
            polygon2: Second polygon

        Returns:
            Polyline3D are equal
        """
    def __repr__(self) -> str:
        """Convert to string
        """

class Polygon3DList():
    """List for Polygon3D objects
    """
    def __contains__(self, value: Polygon3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Polygon3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Polygon3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Polygon3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Polygon3DList:
        """Add a list

        Args:
            eleList: Polygon3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Polygon3D):
        """Constructor with a Polygon3D

        Args:
            ele: Polygon3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Polygon3D

        Args:
            eleList: Polygon3D list
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
    def __setitem__(self, index: (int | slice), value: Polygon3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Polygon3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Polygon3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Polygon3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class PolygonalArea():

    def AppendEdge(self, edge: GeometryEdge) -> eGeometryErrorCode:
        """Append edge (appendPolygonEdge).

        Args:
            edge: Appended edge.

        Returns:
            Error code.
        """
    def GetComponentsCount(self) -> int:
        """Get count of components.

        Returns:
            Count of component.
        """
    def GetEdge(self, edgeIndex: int) -> tuple:
        """Get edge.

        Args:
            edgeIndex: index of the edge.

        Returns:
            Error code.,
            edge of polygon.
        """
    def GetEdges(self) -> tuple:
        """Get copy of all edges.

        Returns:
            Error code.,
            vector of all edges.
        """
    def GetEdgesCount(self) -> int:
        """Get count of edges.

        Returns:
            Count of edges.
        """
    def GetLoopEndEdgeIndex(self, loopIndex: int) -> int:
        """Get the index of last edge of a loop.

        Args:
            loopIndex: index of loop.

        Returns:
            Index of the last edge of the loop identified by the loopIndex value.
        """
    def GetLoopsCount(self) -> int:
        """Get Count of loops.

        Returns:
            Count of loops.
        """
    def GetNeighborEdges(self, edgeIndex: int) -> tuple:
        """Get neighbor edges.

        Args:
            edgeIndex: edge index.

        Returns:
            Error code.,
            previous edge (edge which is before edge[index] in the chain).,
            next edge (edge which is after edge[index] in the chain).
        """
    def GetNextEdge(self, edgeIndex: int) -> tuple:
        """Get next edge.

        Args:
            edgeIndex: edge index.

        Returns:
            Error code.,
            next edge (edge which is after edge[index] in the chain).
        """
    def GetPlane(self) -> tuple:
        """Get plane if polygon is plane.

        Returns:
            Error code.,
            polygon plane.
        """
    def GetPrevEdge(self, edgeIndex: int) -> tuple:
        """Get previous edge.

        Args:
            edgeIndex: edge index.

        Returns:
            Error code.,
            previous edge (edge which is before edge[index] in the chain).
        """
    def GetVector(self) -> tuple:
        """Get Normal vector if polygon is plane.

        Returns:
            Error code.,
            normal vector to the polygon plane.
        """
    def GetVerticesCount(self) -> int:
        """Get count of vertices.

        Returns:
            Count of vertices.
        """
    def SetPlane(self, plane: Plane3D):
        """Set plane.

        Args:
            plane: plane which will be set.
        """
    def SetVector(self, vec: Vector3D) -> eGeometryErrorCode:
        """Set normal vector.

        Args:
            vec: vector which will be set.

        Returns:
            Error code.
        """

class PolygonalArea2D(PolygonalArea):
    """2D polygonal area
    class for 2D polygonal area geometry
    """
    def AppendRelVertex(self, vertex: Point2D) -> tuple:
        """Append vertex in local coordinate system.

        Warning: method does not update edges.

        Args:
            vertex: vertex in local coordinate system which will be appended.

        Returns:
            Error code.,
            index of vertex
        """
    def AppendVertex(self, vertex: Point2D) -> tuple:
        """Append vertex in World coordinate system.

        Warning: method does not update edges.

        Args:
            vertex: vertex in world coordinate system which will be appended.

        Returns:
            Error code.,
            index of vertex
        """
    def EqualRef(self, polygon: PolygonalArea2D) -> bool:
        """Test for equal reference points.

        Args:
            polygon: polygon for comparision.

        Returns:
            True if reference points are equal else return false.
        """
    def GetEdgeVertices(self, edgeIndex: int) -> tuple:
        """Get edge vertices.

        Args:
            edgeIndex: edge index.

        Returns:
            Error code.,
            start point of the edge in world coordinate system.,
            end point of the edge in world coordinate system.
        """
    def GetPolygon(self) -> tuple:
        """Get polygon.

        Old interface: pgon_to_punkte

        Returns:
            Error code.,
            polygon.
        """
    def GetRefPoint(self) -> Point2D:
        """Get the reference point.

        Returns:
            constant reference to point.
        """
    def GetRelVertex(self, vertexIndex: int) -> tuple:
        """Get vertex in Local coordinate system.

        Args:
            vertexIndex: vertex index.

        Returns:
            Error code.,
            vertex in local coordinate system.
        """
    def GetVertex(self, vertexIndex: int) -> tuple:
        """Get vertex in World coordinate system.

        Args:
            vertexIndex: vertex index.

        Returns:
            Error code.,
            vertex in world coordinate system.
        """
    def SetRefPoint(self, refPoint: Point2D) -> eGeometryErrorCode:
        """Set reference point in world coordinate system.

        Coordinates of points will be recalculated with new reference point.

        Args:
            refPoint: new reference point.

        Returns:
            Error code.
        """
    def __eq__(self, polygonalArea: PolygonalArea2D) -> object:
        """Comparison of polygonalAreas without tolerance.

        Be careful, this method work without tolerance!

        Args:
            polygonalArea:Compared polygonalArea.

        Returns:
            True when polygonalAreas are equal, otherwise false.
        """
    def __getitem__(self, vertexIndex: int) -> Point2D:
        """Get point at position from index. Used world coordinates.

        Args:
            vertexIndex: vertex index.

        Returns:
            Copy of vertex[vertexIndex] in world coordinates.
        """
    @typing.overload
    def __iadd__(self, polygonalarea: PolygonalArea2D) -> object:
        """Append polygon.

        Args:
            polygonalarea: polygonal area which will be appended.

        Returns:
            Reference to PolygonalArea2D.
        """
    @typing.overload
    def __iadd__(self, polygon: Polygon2D) -> object:
        """Append loop.

        Args:
            polygon: polygon which will be appended.

        Returns:
            Reference to PolygonalArea2D.
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, verticesCount: int, edgesCount: int):
        """Default constructor.

        Create initialized 2D polygonal area with expected vertices and edges count.
        """
    @typing.overload
    def __init__(self, refPoint: Point2D, verticesCount: int, edgesCount: int):
        """Default constructor.

        Create initialized 2D polygonal area with expected vertices and edges count.
        """
    @typing.overload
    def __init__(self, polygon: PolygonalArea2D):
        """Copy constructor.

        Args:
            polygon: 2D polygon which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix2D) -> object:
        """Matrix transformation.

        Args:
            matrix: point index.

        Returns:
            Transformed 2D polygonal area.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def RefPoint(self) -> None:
        """Get and set the reference point in world coordinate system as property

        :type: None
        """

class PolygonalArea2DList():

    def __contains__(self, value: PolygonalArea2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: PolygonalArea2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> PolygonalArea2D:
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
    def __setitem__(self, index: (int | slice), value: PolygonalArea2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: PolygonalArea2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: PolygonalArea2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class PolygonalArea3D(PolygonalArea):
    """3D polygonal area
    class for 3D polygonal area geometry
    """
    def AppendRelVertex(self, vertex: Point3D) -> tuple:
        """Append vertex in local coordinate system.

        Warning: method does not update edges.

        Args:
            vertex: vertex in local coordinate system which will be appended.

        Returns:
            Error code.,
            index of vertex
        """
    def AppendVertex(self, vertex: Point3D) -> tuple:
        """Append vertex in World coordinate system.

        Warning: method does not update edges.

        Args:
            vertex: vertex in world coordinate system which will be appended.

        Returns:
            Error code.,
            index of vertex
        """
    def EqualRef(self, polygon: PolygonalArea3D) -> bool:
        """Test for equal reference points.

        Args:
            polygon: polygonal area for comparision.

        Returns:
            True if reference points are equal else return false.
        """
    def GetEdgeVertices(self, edgeIndex: int) -> tuple:
        """Get edge vertices.

        Args:
            edgeIndex: edge index.

        Returns:
            Error code.,
            start point of the edge in world coordinate system.,
            end point of the edge in world coordinate system.
        """
    def GetPolygon(self) -> tuple:
        """Get polygon.

        Returns empty polygon, if it has zero edges.

        Returns:
            Error code.,
            polygon.
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point.

        Returns:
            constant reference to point.
        """
    def GetRelVertex(self, vertexIndex: int) -> tuple:
        """Get vertex in Local coordinate system.

        Args:
            vertexIndex: vertex index.

        Returns:
            vertex in local coordinate system.
        """
    def GetVertex(self, vertexIndex: int) -> tuple:
        """Get vertex in World coordinate system.

        Args:
            vertexIndex: vertex index.

        Returns:
            Error code.,
            vertex in world coordinate system.
        """
    def Reverse(self) -> eGeometryErrorCode:
        """Reverse the point order of boundary polygons of the area.

        Returns:
             Error code.
        """
    def SetRefPoint(self, refPoint: Point3D) -> eGeometryErrorCode:
        """Set reference point in world coordinate system.

        Coordinates of points will be recalculated with new reference point.

        Args:
            refPoint: new reference point.
            or:code.
        """
    def __eq__(self, polygonalArea: PolygonalArea3D) -> object:
        """Comparison of polygonalAreas without tolerance.

        Be careful, this method work without tolerance!

        Args:
            polygonalArea:Compared polygonalArea.

        Returns:
            True when polygonalAreas are equal, otherwise false.
        """
    def __getitem__(self, arg2: int) -> Point3D:
        """Get point at position from index. Used world coordinates.

        Args:
            vertexIndex: vertex index.

        Returns:
            Copy of vertex[vertexIndex] in world coordinates.
        """
    @typing.overload
    def __iadd__(self, polygonalarea: PolygonalArea3D) -> object:
        """Append polygon.

        Args:
            polygonalarea: polygonal area which will be appended.

        Returns:
            Reference to PolygonalArea3D.
        """
    @typing.overload
    def __iadd__(self, polygon: Polygon3D) -> object:
        """Append loop.

        Args:
            polygon: polygonal area which will be appended.

        Returns:
            Reference to PolygonalArea3D.
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, verticesCount: int, edgesCount: int):
        """Default constructor.

        Create initialized 3D polygonal area with expected vertices and edges count.
        """
    @typing.overload
    def __init__(self, refPoint: Point3D, verticesCount: int, edgesCount: int):
        """Default constructor.

        Create initialized 3D polygonal area with expected vertices and edges count.
        """
    @typing.overload
    def __init__(self, polygon: PolygonalArea3D):
        """Copy constructor.

        Args:
            polygon: 3D polygonal area which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> object:
        """2D matrix transformation.

        Args:
            matrix: 2D transformation matrix.

        Returns:
            Transformed 3D polygon area.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix3D) -> object:
        """3D matrix transformation.

        Args:
            matrix: 3D transformation matrix.

        Returns:
            Transformed 3D polygon area.
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """
    @property
    def RefPoint(self) -> None:
        """Get and set the reference point in world coordinate system as property

        :type: None
        """

class PolygonalArea3DList():

    def __contains__(self, value: PolygonalArea3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: PolygonalArea3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __getitem__(self, index: int) -> PolygonalArea3D:
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
    def __setitem__(self, index: (int | slice), value: PolygonalArea3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: PolygonalArea3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: PolygonalArea3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Polyhedron3D():
    """Representation class for 3D polyhedron.

    Polyhedron3D represents a 3D solid defined by vertices, edges and faces.
    Polyhedron includes table of vertices, table of edges and table of faces.
    Each table is zero based indexed. Edge is defined via GeometryEdge as
    two indices into vertices table. Geometry edge is default oriented from
    start to end index.
    Face is defined via PolyhedronFace as a vector of oriented edges.
    Oriented edge (OrientedEdge) has EdgeHandle and orientation flag.
    EdgeHandle is index into polyhedron table of all edges, it mean that values
    of EdgeHandle can be from range [0..EdgesCount-1]. This handle can be
    increased and decreased in standard way. When orientation flag is true,
    then orientation is same as GeometryEdge (from Start to End index), if flag is false then
    orientation is backward (from End to Start index).
    """
    def AppendEdge(self, edge: GeometryEdge) -> eGeometryErrorCode:
        """Append edge

        Method throw exception if object is not initialized.
        Old interface: appendPolyederEdge

        Args:
            edge: Appended edge.

        Returns:
            Error code.
        """
    @typing.overload
    def Clear(self):
        """Clear all vertices, edges and faces

        Type and vertices,edges,faces preallocation size of polyhedron will be preserved
        """
    @typing.overload
    def Clear(self, verticesCount: int, edgesCount: int, facesCount: int, negativeOrientation: bool):
        """Clear all vertices, edges and faces

        The "Count" parameters have sense only for appropriate polyhedron type and
        specified a memory allocation size - performance optimization.
        In case of any error, constructor throw an exception.

        Args:
            verticesCount:       Count of expected vertices.
            edgesCount:          Count of expected edges.
            facesCount:          Count of expected faces.
            negativeOrientation: True for negative orientation.
        """
    def Clear(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    @typing.overload
    def CreateCuboid(p1: Point3D, p2: Point3D) -> Polyhedron3D:
        """static constructor for cuboid

        Args:
            p1: lower point of min/max box that states the cuboid's size
            p2: lower point of min/max box that states the cuboid's size
        """
    @staticmethod
    @typing.overload
    def CreateCuboid(box: MinMax3D) -> Polyhedron3D:
        """static constructor for cuboid

        Args:
            box: min/max box that states the cuboid's size
        """
    @staticmethod
    @typing.overload
    def CreateCuboid(placement: AxisPlacement3D, length: float, width: float, height: float) -> Polyhedron3D:
        """Create Polyhedron3D as cuboid

        Args:
            placement: cuboid origin
            length:    length in its x axis
            width:     width in its y axis
            height:    height in its z axis

        Returns:
            created geometry
        """
    @staticmethod
    @typing.overload
    def CreateCuboid(length: float, width: float, height: float) -> Polyhedron3D:
        """Create a cuboid

        Args:
            length: Length
            width:  Width
            height: Height

        Returns:
            Polyhedron3D
        """
    def CreateCuboid(self):
        """ Overloaded function. See individual overloads.
        """
    def CreateFace(self, expectedEdges: int) -> PolyhedronFace:
        """Create face and append it to polyhedron

        Method throw exception if object is not initialized.
        Old interface: appendPolyederFace

        Args:
            expectedEdges: Appended face.

        Returns:
            Created face.
        """
    def DeleteEdge(self, edgeHandle: int) -> eGeometryErrorCode:
        """Delete edge

        Method throw exception if object is not initialized.
        Old interface: deletePolyederEdge

        Args:
            edgeHandle: Edge to delete

        Returns:
            Error code.
        """
    def DeleteFace(self, faceIndex: int) -> eGeometryErrorCode:
        """Delete face at specified position

        Method throw exception in case of any error.
        Old interface: deleteFace

        Args:
            faceIndex: Position of the deleted face. Zero based.

        Returns:
            Error code.
        """
    def DeleteFaces(self, faceIndices: NemAll_Python_Utility.VecSizeTList) -> eGeometryErrorCode:
        """Delete faces at specified positions

        Method throw exception in case of any error.
        Old interface: deleteFace

        Args:
            faceIndices: Positions of the deleted faces. Zero based.

        Returns:
            Error code.
        """
    def EqualRef(self, polyhedron: Polyhedron3D) -> bool:
        """Test for equal reference point

        Args:
            polyhedron: Tested polyhedron.

        Returns:
            True when both polyhedrons has the same reference point.
        """
    @typing.overload
    def GetEdge(self, edgeHandle: int) -> tuple[eGeometryErrorCode, GeometryEdge]:
        """Get edge at the specified position

        Args:
            edgeHandle: Specified position of the edge.

        Returns:
            tuple(Error code.,
                  Filled edge)
        """
    @typing.overload
    def GetEdge(self, orientedEdge: OrientedEdge) -> tuple[eGeometryErrorCode, GeometryEdge]:
        """Get edge at the specified position with orientation

        Args:
            orientedEdge: Specified position and orientation of the edge.

        Returns:
            tuple(Error code.,
                  Filled edge)
        """
    def GetEdge(self):
        """ Overloaded function. See individual overloads.
        """
    def GetEdgeVertices(self, orientedEdge: OrientedEdge) -> tuple[eGeometryErrorCode, Point3D, Point3D]:
        """Get points on specified edge from specified face

        Method throw exception in case of any error.

        Args:
            orientedEdge: Oriented edge.

        Returns:
            tuple(Error code.,
                  StartVertex,
                  EndVertex)
        """
    def GetEdges(self) -> tuple[eGeometryErrorCode, list[GeometryEdge]]:
        """Get copy of all edges

        Old interface: getPolyederAllEdges

        Returns:
            tuple(Error code.,
                  in Vector of edges)
        """
    def GetEdgesCount(self) -> int:
        """Get count of edges

        Method throw exception in case of any error.
        Count

        Returns:
            Count of edges.
        """
    def GetEdgesLines(self) -> tuple[eGeometryErrorCode, Line3DList]:
        """Get copy of all edges as vector of lines

        Returns:
            tuple(Error code.,
                  edges in Vector of lines)
        """
    def GetEdgesOnFaceCount(self, faceIndex: int) -> int:
        """Get count of edges at the specified face

        Method throw exception in case of any error.
        In case of error, return 0.
        Count

        Args:
            faceIndex: Specified position of the face.

        Returns:
            Count if edges.
        """
    def GetFace(self, faceIndex: int) -> PolyhedronFace:
        """Get face at the specified position

        In case of error, method throw an exception.

        Args:
            faceIndex: Specified position of the face.

        Returns:
            Face.
        """
    def GetFacesCount(self) -> int:
        """Get count of faces

        Method throw exception in case of any error.

        Returns:
            Count of faces.
        """
    def GetNormalVectorOfFace(self, faceIndex: int) -> tuple[eGeometryErrorCode, Vector3D]:
        """Get normal vector of the face

        Args:
            faceIndex: face index

        Returns:
            tuple(error code,
                  result normal vector)
        """
    def GetParts(self) -> tuple[eGeometryErrorCode, list[Polyhedron3D]]:
        """Get separated parts (continuos shells)

        Returns:
            tuple(error code,
                  separated bodies)
        """
    def GetPartsCount(self) -> int:
        """Get number of parts in this polyhedron

        Returns:
            number of parts
        """
    def GetRefPoint(self) -> Point3D:
        """Get the reference point

        Returns:
            Constant reference point.
        """
    def GetRelVertex(self, index: int) -> tuple[eGeometryErrorCode, Point3D]:
        """Get relative vertex at specified position

        Method throw exception in case of any error. (usually out of range)

        Args:
            index: Specified position.

        Returns:
            tuple(Error code,
                  out Vertex in Local coordinate system)
        """
    def GetType(self) -> PolyhedronType:
        """Get polyhedron type

        In case of error, method return tEdges.

        Returns:
            Type.
        """
    def GetVertex(self, vertexIndex: int) -> tuple[eGeometryErrorCode, Point3D]:
        """Get vertex at specified position

        Method throw exception in case of any error.

        Args:
            vertexIndex: Specified position of vertex.

        Returns:
            tuple(Error code.,
                  in Vertex at specified position in World coordinate system)
        """
    def GetVertices(self) -> Point3DList:
        """Get copy of vertices in world coordinate system

        Returns:
            Vector with all vertices as Point3D
        """
    def GetVerticesCount(self) -> int:
        """Get count of vertices

        Method throw exception in case of any error.
        Count

        Returns:
            Count of vertices.
        """
    def Heal(self) -> eGeometryErrorCode:
        """Heal polyhedron by splitting non-planar faces to triangles

        Returns:
            error code
        """
    def Invert(self) -> eGeometryErrorCode:
        """Invert polyhedron from positive to negative or vice versa

        Returns:
            error code
        """
    def InvertWithFlagUnchanged(self) -> eGeometryErrorCode:
        """Invert polyhedron from positive to negative or vice versa, but keep flag unchanged

        Returns:
            error code
        """
    def IsNegative(self) -> bool:
        """Checking the negative orientation

        Method throw exception in case of any error.
        Old interface: getPolyederNega

        Returns:
            True when negative orientation, otherwise false.
        """
    def IsValid(self) -> bool:
        """Checking validity

        Depends on polyhedron type

        Returns:
            True when valid, otherwise false.
        """
    def Normalize(self, normType: int) -> eGeometryErrorCode:
        """Normalize polyhedron

        normType:
         0-dim.: keine Kanten oder Flaechen vorhanden
         1-dim.: nur Kanten vorhanden
         2-dim.: Flaechen vorhanden, die aber keine
                 geschlossene Volumenoberflaeche bilden
         3-dim.: Flaechen bilden geschlossene Volumen-
                 oberflaeche

         Method throw exception if object is not initialized.

        Args:
            normType: Type of normalization.

        Returns:
            Error code.
        """
    def ReadFromStream(self, sstream_str: str) -> eGeometryErrorCode:
        """Read Polyhedron3D from stream

        Args:
            sstream_str: input stream

        Returns:
            error code
        """
    def RemapVertices(self, source: Polyhedron3D) -> bool:
        """set vertex order as in source polyhedron

        Args:
            source: -  original cuboid

        Returns:
            success
        """
    def Set(self, refPoint: Point3D, polyhedronWorld: Polyhedron3D):
        """Set polyhedron on reference point. Polyhedron is in world coordinate system

        Args:
            refPoint:        Reference point.
            polyhedronWorld: Polyhedron with vertices in World coordinate system.
        """
    def SetRefPoint(self, refPoint: Point3D):
        """Set the reference point

        Be aware: All vertices will be recalculated on new reference point.
        This operation is very slow in case of many vertices.
        Use constructor for better and faster initialization object.

        Args:
            refPoint: New reference point.
        """
    def SetType(self, polyheronType: PolyhedronType):
        """Get polyhedron type

        Method throw exception if polyhedron is not initialized.
        In case of incorrect polyhedronType, tEdges type will be set.

        Args:
            polyheronType: Type of polyhedron.
        """
    def WriteToStream(self) -> tuple[eGeometryErrorCode, str]:
        """Write Polyhedron3D to the stream

        Returns:
            tuple(error code,
                  output stream)
        """
    def __eq__(self, polyhedron: Polyhedron3D) -> object:
        """Comparison of polyhedrons without tolerance.

        Be careful, this method work without tolerance!

        Args:
            polyhedron: Compared polyhedron.

        Returns:
            True when polyhedrons are equal, otherwise false.
        """
    def __getitem__(self, index: int) -> Point3D:
        """Get vertex at the specified position from index. Used world coordinates

        Operator throw exception in case of any error.

        Args:
            index: Specified position

        Returns:
            Vertex
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, polyhedronType: PolyhedronType, verticesCount: int, edgesCount: int, facesCount: int, negativeOrientation: bool):
        """Constructor

        The "Count" parameters have sense only for appropriate polyhedron type and
        specified a memory allocation size - performance optimization.
        In case of any error, constructor throw an exception.

        Args:
            polyhedronType:      Polyhedron type - edges, faces or volume.
            verticesCount:       Count of expected vertices.
            edgesCount:          Count of expected edges.
            facesCount:          Count of expected faces.
            negativeOrientation: True for negative orientation.
        """
    @typing.overload
    def __init__(self, polyhedron: Polyhedron3D):
        """Copy constructor

        Args:
            polyhedron: Polyhedron which will be copied.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix3D) -> Polyhedron3D:
        """Matrix transformation of vertices

        Args:
            matrix: Transformation matrix.

        Returns:
            Transformed polyhedron.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def RefPoint(self) -> Point3D:
        """Get the reference point


        Be aware: All vertices will be recalculated on new reference point.
        This operation is very slow in case of many vertices.
        Use constructor for better and faster initialization object.
        """
    @RefPoint.setter
    def RefPoint(self, refPoint: Point3D) -> None:
        """Set the reference point

        Be aware: All vertices will be recalculated on new reference point.
        This operation is very slow in case of many vertices.
        Use constructor for better and faster initialization object.

        Args:
            refPoint: New reference point.
        """
    @property
    def Type(self) -> PolyhedronType:
        """Get polyhedron type

        In case of error, method return tEdges.

        Get polyhedron type

        Method throw exception if polyhedron is not initialized.
        In case of incorrect polyhedronType, tEdges type will be set.
        """
    @Type.setter
    def Type(self, polyheronType: PolyhedronType) -> None:
        """In case of error, method return tEdges.


        Method throw exception if polyhedron is not initialized.
        In case of incorrect polyhedronType, tEdges type will be set.

        Args:
            polyheronType: Type of polyhedron.
        """

class Polyhedron3DBuilder():
    """3D polyhedron builder
    """
    def AppendVertex(self, vertex: Point3D) -> tuple:
        """Append new vertex

        Args:
            vertex: Point in world coordinate system

        Returns:
            eOK if success,
            Index where vertex has been inserted
        """
    def Complete(self) -> eGeometryErrorCode:
        """Finalize polyhedron

        Recalculate cached minmax of modified polyhedron
        """
    def SetVertex(self, vertexIndex: int, vertex: Point3D) -> eGeometryErrorCode:
        """Set vertex at the given index

        Args:
            vertexIndex: Index of updated vertex
            vertex:      Point in world coordinate system

        Returns:
            eOK if success
        """
    def __init__(self, polyhedron: Polyhedron3D):
        """Constructor

        Args:
            polyhedron:Polyhedron where vertices will be modified
        """

class Polyhedron3DList():
    """List for Polyhedron3D objects
    """
    def __contains__(self, value: Polyhedron3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Polyhedron3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Polyhedron3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Polyhedron3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Polyhedron3DList:
        """Add a list

        Args:
            eleList: Polyhedron3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Polyhedron3D):
        """Constructor with a Polyhedron3D

        Args:
            ele: Polyhedron3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Polyhedron3D

        Args:
            eleList: Polyhedron3D list
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
    def __setitem__(self, index: (int | slice), value: Polyhedron3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Polyhedron3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Polyhedron3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Polyhedron3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class PolyhedronFace():
    """Polyhedron face
    All constructors are prohibited, only Polyhedron3D can instantiate this class.
    This behavior is dependant on old %Allplan architecture and can be changed.
    """
    @typing.overload
    def AppendEdge(self, edgeHandle: int, positiveOrientation: bool):
        """Append edge into face

        Args:
            edgeHandle:          Appended EdgeHandle.
            positiveOrientation: True for positive, false for negative orientation.
        """
    @typing.overload
    def AppendEdge(self, edge: OrientedEdge):
        """Append edge into face

        Args:
            edge: Appended Edge.
        """
    def AppendEdge(self):
        """ Overloaded function. See individual overloads.
        """
    def AppendEdges(self, edges: OrientedEdgeList):
        """Append edges into face

        Args:
            edges: Vector of edges.
        """
    def GetEdge(self, edgeIndex: int) -> tuple:
        """Get the edge index on specified position

        Old interface: getFaceEdge

        Args:
            edgeIndex: Specified position in edge vector.

        Returns:
            False when edgeIndex is out of range or when occurred another error, otherwise true.,
            Edge index.
        """
    def GetEdges(self) -> OrientedEdgeList:
        """Get the edge index on specified position

        Returns:
            Vector of oriented edges.
        """
    def GetEdgesCount(self) -> int:
        """Get count of edges

        Old interface: getFaceEdgeCount

        Returns:
            Count of edges.
        """
    def GetFlags(self) -> int:
        """Get the flags of the face

        Returns:
            Face flags.
        """
    def SetFlags(self, flags: int):
        """Set the flags of the face

        Args:
            flags: Face flags.
        """
    def __getitem__(self, edgeIndex: int) -> OrientedEdge:
        """Get the edge index on specified position

        Method can throw exception when index is out of range.
        Please use the GetEdgeIndex with return flag when you do not used exception handler.
        Old interface: getFaceEdge

        Args:
            edgeIndex: Specified position in edge vector.

        Returns:
            Edge index, not reference.
        """
    def __init__(self, face: PolyhedronFace):
        """Standard copy constructor

        Args:
            face
        """
    def __repr__(self) -> str:
        """Convert the list to a string

        Returns:
            List values as string
        """

class PolyhedronType(enum.Enum):
    """Type of polyhedron visual representation

    tInvalid:
    tEdges  : Polyhedron has a edges only.
    tFaces  : Polyhedron has a faces.
    tVolume : Polyhedron has a volume.
    """

    names = {tInvalid: tInvalid,
             tEdges: tEdges,
             tFaces: tFaces,
             tVolume: tVolume}
    tEdges = 1
    tFaces = 2
    tInvalid = 0
    tVolume = 3

    values = {0: tInvalid,
              1: tEdges,
              2: tFaces,
              3: tVolume}

    def __getitem__(self, key: (str | int | float)) -> PolyhedronType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class PolyhedronUtil():
    """Polyhedron utilities
    """
    @staticmethod
    def CalcMatrix2GroundView(inputPolyhedron: Polyhedron3D, faceIndex: int) -> tuple[eGeometryErrorCode, Matrix3D]:
        """Calculates the 3DMatrix that is neccessary to project the Face of a polyhedron onto a groundview. It considers the orientation of the normalvector. so the bottom face of a cuboid has different matrix then the top face (turnd 180)
        Function is token from old Allplan classic Geomatry calculations

        Args:
            inputPolyhedron: The Polyhedron with the requested face
            faceIndex:       The faceindex we that has to be projected into Groundview

        Returns:
            tuple(Ok or Error,
                  The resul tmatrix. Calc the coords of the poyhedron with that matrix and you get the projection to groundview so that the requested face is complanar to Ground view)
        """
    @staticmethod
    def GetFacePoints(elem: Polyhedron3D, face: PolyhedronFace) -> tuple[bool, NemAll_Python_Utility.VecSizeTList, Point3DList]:
        """Get the points of a polyhedron face

        Args:
            elem: Get the points from this polyhedron
            face: Get the points from this face

        Returns:
            tuple(true, if the extraction went well,
                  Vertices of the faces points,
                  Resulting points)
        """
    @staticmethod
    def GetFootprint(polyhedron: Polyhedron3D) -> Polygon2D:
        """Get footprint of polyhedron

        Args:
            polyhedron: Polyhedron

        Returns:
            Footprint polygon
        """
    @staticmethod
    @typing.overload
    def GetNextEdge(elem: Polyhedron3D, face: PolyhedronFace) -> tuple[bool, NemAll_Python_Utility.VecSizeTList, Point3DList]:
        """Get the next connected edge

        Args:
            elem: Get the vertices for a face of this polyhedron
            face: Get the vertices of this face

        Returns:
            tuple(true if returned values are valid,
                  Vertices of the already added faces points,
                  Already added faces points)
        """
    @staticmethod
    @typing.overload
    def GetNextEdge(elem: Polyhedron3D, edges: GeometryEdgeList, verticeHandle: int) -> tuple[bool, NemAll_Python_Utility.VecSizeTList,
                    Point3DList]:
        """Get the last connected edge

        Args:
            elem:          Get the vertices for a face of this polyhedron
            edges:         All edges from the given polyhedron
            verticeHandle: Vertice index of the last added point

        Returns:
            tuple(true if returned values are valid,
                  Vertices of the already added faces points,
                  Already added polyhedron points)
        """
    def GetNextEdge(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def MergePlanarFaces(polyhedron: Polyhedron3D):
        """Merge planar faces

        Args:
            polyhedron: Polyhedron to modify
        """
    @staticmethod
    @typing.overload
    def ReorderPolyhedronFaces(polyhedron: Polyhedron3D, bottomPlane: Plane3D, topPlane: Plane3D):
        """Reorder polyhedron faces according to planes.

        Reorders given\p polyhedron faces according to planes. The face laying
        in  bottomPlane goes first and face laying in\p topPlane goes second.
        Order of other faces is not guaranteed.

        Old interface: normalizeArchitectural3d

        Args:
            polyhedron:  Polyhedron.
            bottomPlane: Bottom plane.
            topPlane:    Top plane.
        """
    @staticmethod
    @typing.overload
    def ReorderPolyhedronFaces(polyhedron: Polyhedron3D, direction: Vector3D):
        """Reorder polyhedron faces according to direction.

        Reorders given\p polyhedron faces according to given direction.
        The face with normal most similar to the direction goes first
        and face with normal most opposite to the direction goes second.
        Order of other faces is not guaranteed.

        Args:
            polyhedron: Polyhedron.
            direction:  Direction vector for face ordering.
        """
    def ReorderPolyhedronFaces(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def RepairFaceNormals(polyhedron: Polyhedron3D) -> tuple[eGeometryErrorCode, Polyhedron3D, bool]:
        """Create solid polyhedron from closed sheet or void

        Args:
            polyhedron: Polyhedron

        Returns:
            tuple(Error code,
                  Polyhedron,
                  Flag whether polyhedron was changed)
        """
    @staticmethod
    def RepairPolyhedron(polyhedron: Polyhedron3D) -> tuple[bool, bool, bool, eGeometryErrorCode, Polyhedron3D]:
        """Repair a polyhedron

        Args:
            polyhedron: Polyhedron

        Returns:
            tuple(cross loop changed, split faces at edged changed, normals changed, geometry error code,
                  Polyhedron)
        """
    @staticmethod
    def RepairPolyhedronCrossLoopFaces(polyhedron: Polyhedron3D) -> eGeometryErrorCode:
        """Repair cross loop (8-shaped) faces in polyhedron

        Args:
            polyhedron: Polyhedron

        Returns:
            Error code
        """
    @staticmethod
    def SimplifyPolyhedron(polyhedron: Polyhedron3D) -> bool:
        """Simplify polyhedron

        Args:
            polyhedron: Polyhedron to simplify

        Returns:
            true if simplification is successful
        """
    @staticmethod
    def SplitFacesAtEdges(polyhedron: Polyhedron3D) -> tuple[eGeometryErrorCode, Polyhedron3D, bool]:
        """Split faces at edges from another faces

        Args:
            polyhedron: Polyhedron to modify

        Returns:
            tuple(Error code,
                  Polyhedron to modify,
                  Flag whether polyhedron was changed)
        """
    @staticmethod
    def SplitNonPlanarFaces(polyhedron: Polyhedron3D, mergePlanarFaces: bool = True) -> bool:
        """Split non-planar faces

        Args:
            polyhedron:       Polyhedron to modify
            mergePlanarFaces: Flag whether planar faces should be merged

        Returns:
            true if polyhedron modified
        """
    @staticmethod
    def TryToNormalizePolyhedron(polyhedron: Polyhedron3D) -> tuple[bool, Polyhedron3D]:
        """Try to normalize polyhedron

        Args:
            polyhedron: Polyhedron

        Returns:
            nullopt if the polyhedron is valid(already normalized) or not possible to normalize, otherwise it returns normalized polyhedron
        """

class Polyline2D(PolyPoints2D):
    """Representation class for 2D Polyline.
    """
    def GetLine(self, index: int) -> Line2D:
        """Extract a line

        Args:
            index: Index of the line

        Returns:
            Line from the index
        """
    def GetLines(self) -> Line2DList:
        """Get all lines from this polyline

        Returns:
            count of extracted lines,
            Vector of extracted lines
        """
    def IsValid(self) -> bool:
        """Check if the polygon is valid ( has at least 2 points )

        For additional point validation use Service::Validate.

        Returns:
            true if is valid
        """
    def LineCount(self) -> int:
        """Get the count of lines connecting the points

        Returns:
            count of lines
        """
    def Reverse(self):
        """Reverse orientation of the Polyline
        """
    def __eq__(self, polyline2: Polyline2D) -> bool:
        """Equal operator

        Args:
            polyline2: Second polyline

        Returns:
            Polyline3D are equal
        """
    @typing.overload
    def __iadd__(self, polyline: Polyline2D) -> Polyline2D:
        """Addition assignment operator

        Args:
            polyline: Polyline which will be added

        Returns:
            Reference to polyline
        """
    @typing.overload
    def __iadd__(self, point: Point2D) -> Polyline2D:
        """Addition assignment operator

        Args:
            point: New Point2D which will be added to the polyline

        Returns:
            Reference to polyline
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, pntList: list):
        """Constructor with an initializer list

        Args:
            pntList: Point list
        """
    @typing.overload
    def __init__(self, polyline: Polyline2D):
        """Copy constructor.

        Args:
            polyline: Polyline which will be copied
        """
    @typing.overload
    def __init__(self, points: Point2DList):
        """Vector points constructor.

        Args:
            points: Vector of points which will be moved to polyline
        """
    @typing.overload
    def __init__(self, polyline: Polyline2D, skip: int, count: int):
        """Copy constructor with limited scope

        Args:
            polyline: Polyline which will be copied
            skip:     count of points ignored at start.
            count:    count of points copied.
        """
    @typing.overload
    def __init__(self, polygon: Polygon2D):
        """Constructor.

        If polygon have two or more components, then constructor throw Geometry exception.

        Args:
            polygon: Polygon2D whose points and reference point will build the new polyline
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, polyline2: Polyline2D) -> bool:
        """Not equal operator

        Args:
            polyline2: Second polyline

        Returns:
            Polyline3D are equal
        """
    def __repr__(self) -> str:
        """Convert to string
        """

class Polyline2DList():
    """List for Polyline2D objects
    """
    def __contains__(self, value: Polyline2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Polyline2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Polyline2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Polyline2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Polyline2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Polyline2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Polyline2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Polyline2DUtil():
    """Implemtation of the utilities for Polyline2D
    """
    @staticmethod
    def AlignSegmentsToBaseSegment(dimensionLine: Polyline2D, indexBaseSegment: int = 1) -> bool:
        """Align the points of the dimension line

        Args:
            dimensionLine:    Dimension line
            indexBaseSegment: Index of the base segment (default = 1)

        Returns:
            true, if all points are aligned
        """
    @staticmethod
    @typing.overload
    def AppendToPolyline2D(polyline: Polyline2D, append: Line2D) -> tuple[bool, Polyline2D, bool, bool]:
        """Appends a line to a polyline the way that the line is always appended at the end

        Args:
            polyline: Polyline to be appended to
            append:   Line to be appended

        Returns:
            tuple(True if successful, false if line is not valid or is not connected to polyline,
                  Resulting polyline,
                  Returns if function has to swap the polyline point order,
                  Returns is function has to swap the appended line/polyline point order)
        """
    @staticmethod
    @typing.overload
    def AppendToPolyline2D(polyline: Polyline2D, append: Polyline2D) -> tuple[bool, Polyline2D, bool, bool]:
        """Appends a line to a polyline the way that the line is always appended at the end

        Args:
            polyline: Polyline to be appended to
            append:   Polyline to be appended

        Returns:
            tuple(True if successful, false if line is not valid or is not connected to polyline,
                  Resulting polyline,
                  Returns if function has to swap the polyline point order,
                  Returns is function has to swap the appended line/polyline point order)
        """
    def AppendToPolyline2D(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def CreatePolyline2D(startPnt: Point2D, endPnt: Point2D, corners: int, diameter: float, systemAngle: float, bCenterPnt: bool,
                         bClockwise: bool) -> tuple[Polyline2D, Point2D]:
        """Create a Polyline2D

        Args:
            startPnt:    Start point
            endPnt:      End point
            corners:     Count of the corners
            diameter:    Contains the diameter of the rectangle
            systemAngle: Angle of the window where the rectangle will be drawn
            bCenterPnt:  point is center point: true/false
            bClockwise:  Determines the direction of rotation

        Returns:
            tuple(2D polyline,
                  Center point)
        """
    @staticmethod
    def GetOutlinePolylineSideFromPoint(polygon: Polygon2D, fromPoint: Point2D, directionPoint: Point2D, axis_object: object) -> tuple[int,
                                        Polyline2D]:
        """Get the outline polygon side by a point

        Args:
            polygon:        Polygon
            fromPoint:      From point
            directionPoint: Direction point
            axis_object:    Axis

        Returns:
            Error code, outline Polyline
        """
    @staticmethod
    def GetPolyline2DSegment(polyline: Polyline2D, clickPoint: Point2D) -> tuple[int, Line2D]:
        """Get the closest segment for the given click point

        Args:
            polyline:   Polyline to analyze
            clickPoint: Click point to analyze

        Returns:
            tuple(Index of the end point of the clicked line,
                  Segment of the polyline, where the click point is on)
        """
    @staticmethod
    def RemoveNonCorners(outline: Polyline2D):
        """Normalize the polygon by removing points, which are no corners

        Args:
            outline: Closed polygon outline of a wall
        """

class Polyline3D(PolyPoints3D):
    """Representation class for 3D Polyline.
    """
    def GetLine(self, index: int) -> Line3D:
        """Extract a line

        Args:
            index: Index of the line

        Returns:
            indexed line
        """
    def GetLines(self) -> Line3DList:
        """get lines from polyline

        Returns:
            lines
        """
    def InsertPolyline(self, polyline: Polyline3D, position: int = 18446744073709551615) -> bool:
        """Insert another polyline at given position

        Args:
            polyline: Polyline to be inserted
            position: Position where the polyline has to be inserted

        Returns:
            true if successful
        """
    def IsPlanar(self) -> tuple[bool, Plane3D]:
        """Check if polyline is on one plane

        Returns:
            tuple(True if polyline is on one plane,
                  if polyline is on one plane the plane is calculated)
        """
    def IsValid(self) -> bool:
        """Check if the polygon is valid ( has at least 2 points )

        For additional point validation use Service::Validate.

        Returns:
            true if is valid
        """
    def LineCount(self) -> int:
        """Get the count of lines connecting the points

        Returns:
            count of lines
        """
    def Reverse(self):
        """Reverse Polyline orientation
        """
    def __eq__(self, polyline2: Polyline3D) -> bool:
        """Equal operator

        Args:
            polyline2: Second polyline

        Returns:
            Polyline3D are equal
        """
    @typing.overload
    def __iadd__(self, polyline: Polyline3D) -> Polyline3D:
        """Additional assignment operator

        Args:
            polyline: Polyline which will be added to current polyline

        Returns:
            Reference to polyline
        """
    @typing.overload
    def __iadd__(self, point: Point3D) -> Polyline3D:
        """Addition assignment operator

        Args:
            point: New Point3D which will be added to the polyline

        Returns:
            Reference to polyline
        """
    @typing.overload
    def __iadd__(self, line: Line3D) -> Polyline3D:
        """Addition assignment operator

        Args:
            line: Line3D which will be added to the polyline

        Returns:
            Reference to polyline
        """
    def __iadd__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, pntList: list[Point3D]):
        """Constructor with an initializer list

        Args:
            pntList: Point list
        """
    @typing.overload
    def __init__(self, polyline: Polyline3D):
        """Copy constructor

        Args:
            polyline: Polyline which will be copied
        """
    @typing.overload
    def __init__(self, polyline: Polyline3D, skip: int, count: int):
        """Copy constructor with limited scope

        Args:
            polyline: Polyline which will be copied
            skip:     count of points ignored at start.
            count:    count of points copied.
        """
    @typing.overload
    def __init__(self, points: Point3DList):
        """Vector points constructor.

        Args:
            points: Vector of points which will be moved to polyline
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __mul__(self, matrix: Matrix3D) -> Polyline3D:
        """Multiple Polyline with matrix

        Args:
            matrix: Transformation matrix

        Returns:
            Transformed polyline
        """
    def __ne__(self, polyline2: Polyline3D) -> bool:
        """Not equal operator

        Args:
            polyline2: Second polyline

        Returns:
            Polyline3D are equal
        """
    def __repr__(self) -> str:
        """Convert to string
        """

class Polyline3DList():
    """List for Polyline3D objects
    """
    def __contains__(self, value: Polyline3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Polyline3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Polyline3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Polyline3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Polyline3DList:
        """Add a list

        Args:
            eleList: Polyline3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Polyline3D):
        """Constructor with a Polyline3D

        Args:
            ele: Polyline3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Polyline3D

        Args:
            eleList: Polyline3D list
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
    def __setitem__(self, index: (int | slice), value: Polyline3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Polyline3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Polyline3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Polyline3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Spline2D(PolyPoints2D):
    """Representation class for 2D spline.
    """
    def GetEndVector(self) -> Vector2D:
        """Get end vector.

        Returns:
            end vector.
        """
    def GetStartVector(self) -> Vector2D:
        """Get start vector.

        Returns:
            start vector.
        """
    def IsClosed(self) -> bool:
        """Check if spline is closed ( first/last points are equal )

        Returns:
            closed spline true/false
        """
    def Reverse(self):
        """Reverse of current spline

        Method reverse Spline using reverse from PolyPoints and swapping tangents.
        """
    def SetEndVector(self, vec: Vector2D):
        """Set end vector.

        Args:
            vec: new end vector.
        """
    def SetStartVector(self, vec: Vector2D):
        """Set start vector.

        Args:
            vec: new start vector.
        """
    def __eq__(self, spline: Spline2D) -> object:
        """Comparison of splines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            spline: Compared spline.

        Returns:
            True when splines are equal, otherwise false.
        """
    @typing.overload
    def __init__(self):
        """Initialize empty spline"""
    @typing.overload
    def __init__(self, spline: Spline2D):
        """Copy constructor.

        Args:
            spline:  Spline which will be copied.
        """
    @typing.overload
    def __init__(self, pntList: typing.List[Point2D]):
        """Default constructor

        Args:
            pntList: list with control points
        """
    def __init__(self):
        """Default constructor

        Args:
            pntList: list with control points
        """
    def __mul__(self, matrix: Matrix2D) -> Spline2D:
        """Multiple Spline with matrix.

        Args:
            matrix: Transformation matrix.

        Returns:
            Transformed spline.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndVector(self) -> Vector2D:
        """Get end vector.
        """
    @EndVector.setter
    def EndVector(self, value: Vector2D) -> None:
        """Set end vector.
        """
    @property
    def StartVector(self) -> Vector2D:
        """Get start vector.
        """
    @StartVector.setter
    def StartVector(self, value: Vector2D) -> None:
        """Set start vector.
        """

class Spline2DList():
    """List for Spline2D objects
    """
    def __contains__(self, value: Spline2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Spline2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Spline2DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Spline2D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Spline2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Spline2D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Spline2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class Spline3D(PolyPoints3D):
    """class for 3D spline geometry
    """
    def CalculateEndVector(self) -> Vector3D:
        """Calculates end vector

        Returns:
            End vector
        """
    @typing.overload
    def CalculatePoint(self, param: float) -> Point3D:
        """Calculates point on spline

        Args:
            param: parameter of spline.

        Returns:
            Resulting point
        """
    @staticmethod
    @typing.overload
    def CalculatePoint(param: float, cpoints: Point3DList) -> Point3D:
        """Calculates point on spline

        Args:
            param:   parameter of spline.
            cpoints: control points of spline.

        Returns:
            Resulting point
        """
    def CalculatePoint(self):
        """ Overloaded function. See individual overloads.
        """
    def CalculateStartVector(self) -> Vector3D:
        """Calculates start vector

        Returns:
            Start vector
        """
    @staticmethod
    def CreateClosedSpline(points: Point3DList) -> Spline3D:
        """Create closed spline from given points

        Args:
            points: Points

        Returns:
            Spline
        """
    def GetControlPoints(self) -> tuple[GeoErrorCode, list[Point3D]]:
        """Compute bezier control points

        Returns:
            tuple(error code,
                  vector of control points)
        """
    def GetEndVector(self) -> Vector3D:
        """Get end vector.

        Returns:
            end vector.
        """
    def GetStartVector(self) -> Vector3D:
        """Get start vector.

        Returns:
            start vector.
        """
    def IsClosed(self) -> bool:
        """Check if spline is closed ( first/last points are equal )

        Returns:
            closed spline true/false
        """
    def IsCollinear(self) -> bool:
        """Function checks if the 3D spline is collinear - all control points are on same line

        Returns:
            true if collinear
        """
    def IsPlanar(self) -> tuple[bool, Plane3D]:
        """Function checks if the 3D spline is planar, if yes sets the plane

        Returns:
            tuple(true if planar,
                  the plane the spline is laying on)
        """
    def Reverse(self):
        """Reverse of current spline

        Method reverse Spline using reverse from PolyPoints and swapping tangents.
        """
    def SetEndVector(self, vec: Vector3D):
        """Set end vector.

        Args:
            vec: new end vector.
        """
    def SetStartVector(self, vec: Vector3D):
        """Set start vector.

        Args:
            vec: new start vector.
        """
    def __eq__(self, spline: Spline3D) -> object:
        """Comparison of splines without tolerance.

        Be careful, this method work without tolerance!

        Args:
            spline:Compared spline.

        Returns:
            True when splines are equal, otherwise false.
        """
    def __iadd__(self, point: Point3D) -> Spline3D:
        """Addition assignment operator

        Args:
            point: New Point3D which will be added to the spline

        Returns:
            Reference to spline
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, splinePoints: list):
        """constructor.

        Args:
            splinePoints
        """
    @typing.overload
    def __init__(self, spline: Spline3D):
        """Copy constructor.

        Args:
            spline: Spline which will be copied.
        """
    @typing.overload
    def __init__(self, spline: Spline2D, zPlane: float):
        """Copy constructor.

        Args:
            spline: Spline which will be copied.
            zPlane: Z plane for the spline
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    @property
    def EndVector(self) -> Vector3D:
        """Get end vector.
        """
    @EndVector.setter
    def EndVector(self, value: Vector3D) -> None:
        """Set end vector.
        """
    @property
    def IsPeriodic(self) -> bool:
        """Check if spline is periodic ( first/last points are equal + start and end tangents are equal)
        """
    @IsPeriodic.setter
    def IsPeriodic(self, value: bool) -> None:
        """Check if spline is periodic ( first/last points are equal + start and end tangents are equal)
        """
    @property
    def StartVector(self) -> Vector3D:
        """Get start vector.
        """
    @StartVector.setter
    def StartVector(self, value: Vector3D) -> None:
        """Set start vector.
        """

class Spline3DList():
    """List for Spline3D objects
    """
    def __contains__(self, value: Spline3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Spline3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Spline3DList) -> bool:
        """Compare two lists
        """
    def __getitem__(self, index: int) -> Spline3D:
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
        """Create a string from the elements of the list
        """
    def __setitem__(self, index: (int | slice), value: Spline3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Spline3D):
        """Append a list item

        Args:
            value: Value to append
        """
    def extend(self, iterable: Spline3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """

class SweepRotationType(enum.Enum):
    """Locked    :
    Unlocked  :
    RailLocked:
    """
    Locked = 0
    RailLocked = 2
    Unlocked = 1

    names = {Locked: Locked,
             Unlocked: Unlocked,
             RailLocked: RailLocked}

    values = {0: Locked,
              1: Unlocked,
              2: RailLocked}

    def __getitem__(self, key: (str | int | float)) -> SweepRotationType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class TangentCalculus():
    """Tangent calculation at an element point
    """
    @staticmethod
    @typing.overload
    def Calculate(line: Line2D) -> Vector3D:
        """Calculates tangent vector of Line2D

        Args:
            line: Line2D on which to calculate tangent vector

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(line: Line3D) -> Vector3D:
        """Calculates tangent vector of Line3D

        Args:
            line: line on which to calculate tangent vector

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline: Polyline2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Polyline2D at given point

        Args:
            polyline: Polyline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(polyline: Polyline3D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Polyline2D at given point

        Args:
            polyline: Polyline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(polygon: Polygon2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Polygon2D at given point

        Args:
            polygon:  Polygon on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Arc2D at given point

        Args:
            arc:      Arc2D on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(arc: Arc3D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Arc3D at given point

        Args:
            arc:      Arc3D on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: Spline2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Spline2D at given point

        Args:
            spline:   Spline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(spline: Spline3D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Spline2D at given point

        Args:
            spline:   Spline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(bspline: BSpline2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of BSpline2D at given point

        Args:
            bspline:  BSpline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(bspline: BSpline3D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of BSpline3D at given point

        Args:
            bspline:  BSpline on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(clothoid: Clothoid2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Clothoid2D at given point

        Args:
            clothoid: Clothoid on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(path: Path2D, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector of Path2D at given point

        Args:
            path:     Path on which to calculate tangent vector
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vector
        """
    @staticmethod
    @typing.overload
    def Calculate(brep: BRep3D, inputPnt: Point3D) -> Vector3DList:
        """Calculates tangent vector of BRep3D at given point

        Args:
            brep:     Brep body
            inputPnt: point on object for tangent calculation

        Returns:
            tangent vectors
        """
    @staticmethod
    @typing.overload
    def Calculate(geoObject: object, inputPnt: Point3D) -> Vector3D:
        """Calculates tangent vector from object at given point

        Args:
            geoObject: object on which to calculate tangent vector
            inputPnt:  point on object for tangent calculation

        Returns:
            tangent vector
        """
    def Calculate(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def CalculateNormal(brep: BRep3D, inputPnt: Point3D) -> Vector3D:
        """Calculates normal vector of BRep3D at given point

        Args:
            brep:     Brep body
            inputPnt: point on object for normal calculation

        Returns:
            normal vector
        """

class TransformCoord():
    """This class offers functions to transform a world point into the local coordinate system (PointLocal)
    defined by a geometry object or a vector of objects. Functions named PointGlobal will take a local point
    and project its coordinates into world coordinates.

    In other words:
    A local point holds the shortest distance from a real world point to an object in its y value.
    Its x value is calculated as the offset from the objects start point to the perpendicular point
    of the real world point.
    """
    @staticmethod
    @typing.overload
    def PointGlobal(path: Path2D, localPoint: Point2D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            path:       Path of 2D geometry objects
            localPoint: Local point with offset as x and distance as y
            eps:        Tolerance for clothoids and splines

        Returns:
             Global point on the path,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(geoObject: object, offset: float, eps: float) -> tuple:
        """Transform the local offset to world coordinates.

        Args:
            geoObject: First IGeometry object
            offset:    Distance from start point
            eps:       Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(path: Path2D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            path:   Path of 2D IGeometry objects
            offset: Distance from start point
            eps:    Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(path: Path3D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            path:   Path of 2D IGeometry objects
            offset: Distance from start point
            eps:    Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(line: Line2D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            line:   Line 2D
            offset: Distance from start point

        Returns:
             Global point on the 2D line
        """
    @staticmethod
    @typing.overload
    def PointGlobal(line: Line2D, localPoint: Point2D) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            line:       Line 2D
            localPoint: Local point

        Returns:
             Global point on the 2D line
        """
    @staticmethod
    @typing.overload
    def PointGlobal(line: Line3D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        emarks    If the object is a 3D line, the correct result would be a 3D circle around the line.
        In this case this function returns the intersection point between the circle and a plane.
        Where the plane is defined by the xy axis and the same z value as the circles center point.

        Args:
            line:   Line 3D
            offset: Distance from start point

        Returns:
             Global point on the 3D Line
        """
    @staticmethod
    @typing.overload
    def PointGlobal(polygon: Polygon3D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            polygon: 3D Polygon
            offset:  Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(polyline: Polyline2D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            polyline: 2D Polyline
            offset:   Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(polyline: Polyline3D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            polyline: 3D Polyline
            offset:   Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(polygon: Polygon2D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            polygon: 2D Polygon
            offset:  Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(arc: Arc2D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            arc:    2D Arc
            offset: Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(arc: Arc2D, localPoint: Point2D) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            arc:        2D Arc
            localPoint: Local point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(arc: Arc3D, offset: float) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            arc:    3D Arc
            offset: Distance from start point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(arc: Arc3D, localPoint: Point2D) -> Point3D:
        """Transform the local coordinates to world coordinates.

        Args:
            arc:        3D Arc
            localPoint: Local point

        Returns:
             Global point on the geometry
        """
    @staticmethod
    @typing.overload
    def PointGlobal(clothoid: Clothoid2D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            clothoid: 2D Clothoid
            offset:   Distance from start point
            eps:      Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(clothoid: Clothoid2D, localPoint: Point2D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            clothoid:   2D Clothoid
            localPoint: Local point
            eps:        Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(spline: Spline2D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        emarks Due to restrictions in the old functions (splin7, splin2) local points
        with a x value smaller than 0 are treated as x=0. If the x value of the
        local point is bigger than the splines length, the length of the spline
        is uses as x value.

        Args:
            spline: 2D Spline
            offset: Distance from start point
            eps:    Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(spline: Spline2D, localPoint: Point2D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        emarks Due to restrictions in the old functions (splin7, splin2) local points
        with a x value smaller than 0 are treated as x=0. If the x value of the
        local point is bigger than the splines length, the length of the spline
        is uses as x value.

        Args:
            spline:     2D Spline
            localPoint: Local Point
            eps:        Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(spline: Spline3D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        emarks Due to restrictions in the old functions (splin7, splin2) local points
        with a x value smaller than 0 are treated as x=0. If the x value of the
        local point is bigger than the splines length, the length of the spline
        is uses as x value.

        Args:
            spline: 3D Spline
            offset: Distance from start point
            eps:    Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(spline: Spline3D, localPoint: Point2D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        emarks Due to restrictions in the old functions (splin7, splin2) local points
        with a x value smaller than 0 are treated as x=0. If the x value of the
        local point is bigger than the splines length, the length of the spline
        is uses as x value.

        Args:
            spline:     3D Spline
            localPoint: Local Point
            eps:        Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(spline: BSpline3D, offset: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            spline: 3D Spline
            offset: Distance from start point

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointGlobal(geoObject: object, localPoint: Point2D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            geoObject:  Geometry object
            localPoint: Local point with offset as x and distance as y
            eps:        Tolerance for clothoids and splines

        Returns:
             Global point on the geometry,
            true if the calculation was successful
        """
    def PointGlobal(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def PointGlobalEx(clothoid: Clothoid2D, offset: float, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        This method compute global point by offset related to axis of clothoid (clothoid with parallel=0).
        This method is faster and computing global point with higher precision.

        Use PointGlobalEx with PointLocalEx cooperation only.

        sa PointLocalEx, TransformClothoidLocalOffset

        Args:
            clothoid: 2D Clothoid
            offset:   Distance from start point on axis curve
            eps:      Tolerance for clothoids and splines

        Returns:
             Global point on the geometry by offset on axis curve,
            Tangent at the Transformed point on the object,
            Curvature at Transformed point on the object,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(path: Path2D, inputPnt: Point3D, eps: float) -> tuple:
        """Transform the local coordinates to world coordinates.

        Args:
            path:     2D Path
            inputPnt: Projection point
            eps:      Tolerance for clothoids and splines

        Returns:
             Local point on the path,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(line: Line2D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 2D line

        Args:
            line:     2D Line
            inputPnt: 3D Projection point

        Returns:
             Local point on the 2D line
        """
    @staticmethod
    @typing.overload
    def PointLocal(line: Line2D, inputPnt: Point2D) -> Point2D:
        """Calculate the local coordinates on a 2D line

        Args:
            line:     2D Line
            inputPnt: 2D Projection point

        Returns:
             Local point on the 2D line
        """
    @staticmethod
    @typing.overload
    def PointLocal(placement: AxisPlacement2D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 2D axis placement

        Args:
            placement: 2D axis placement
            inputPnt:  2D Projection point

        Returns:
             Local point on 2D axis placement
        """
    @staticmethod
    @typing.overload
    def PointLocal(placement: AxisPlacement2D, inputPnt: Point2D) -> Point2D:
        """Calculate the local coordinates on a 2D axis placement

        Args:
            placement: 2D axis placement
            inputPnt:  2D Projection point

        Returns:
             Local point on 2D axis placement
        """
    @staticmethod
    @typing.overload
    def PointLocal(line: Line3D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 3D line

        Args:
            line:     3D Line
            inputPnt: Projection point

        Returns:
             Local point on the 3D line
        """
    @staticmethod
    @typing.overload
    def PointLocal(polyhedron: Polyhedron3D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 3D polyhedron

        Args:
            polyhedron: 3D Polyhedron
            inputPnt:   Projection point

        Returns:
             Local point on the 3D polyhedron
        """
    @staticmethod
    @typing.overload
    def PointLocal(polyline: Polyline3D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 3D polyline

        Args:
            polyline: 3D Polyline
            inputPnt: Projection point

        Returns:
             Local point on the 3D polyline
        """
    @staticmethod
    @typing.overload
    def PointLocal(polyline: Polyline2D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 2D polyline

        Args:
            polyline: 2D Polyline
            inputPnt: Projection point

        Returns:
             Local point on the polyline
        """
    @staticmethod
    @typing.overload
    def PointLocal(polyline: Polyline2D, inputPnt: Point2D) -> Point2D:
        """Calculate the local coordinates on a 2D polyline

        Args:
            polyline: 2D Polyline
            inputPnt: Projection point

        Returns:
             Local point on the polyline
        """
    @staticmethod
    @typing.overload
    def PointLocal(polygon: Polygon2D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 2D polygon

        Args:
            polygon:  2D Polygon
            inputPnt: Projection point

        Returns:
             Local point on the polygon
        """
    @staticmethod
    @typing.overload
    def PointLocal(arc: Arc2D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 2D arc

        Args:
            arc:      2D Arc
            inputPnt: 3D Projection point

        Returns:
             Local point on the 2D arc
        """
    @staticmethod
    @typing.overload
    def PointLocal(arc: Arc2D, inputPnt: Point2D) -> Point2D:
        """Calculate the local coordinates on a 2D arc

        Args:
            arc:      2D Arc
            inputPnt: 2D Projection point

        Returns:
             Local point on the 2D arc
        """
    @staticmethod
    @typing.overload
    def PointLocal(arc: Arc3D, inputPnt: Point3D) -> Point2D:
        """Calculate the local coordinates on a 3D arc

        Args:
            arc:      3D Arc
            inputPnt: 3D Projection point

        Returns:
             Local point on the 3D arc
        """
    @staticmethod
    @typing.overload
    def PointLocal(arc: Arc3D, inputPnt: Point2D) -> Point2D:
        """Calculate the local coordinates on a 3D arc

        Args:
            arc:      3D Arc
            inputPnt: 3D Projection point

        Returns:
             Local point on the 3D arc
        """
    @staticmethod
    @typing.overload
    def PointLocal(clothoid: Clothoid2D, inputPnt: Point2D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D clothoid

        Args:
            clothoid: 2D Clothoid
            inputPnt: Projection point as Point2D
            eps:      Tolerance

        Returns:
             Local point on the 2D clothoid,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(clothoid: Clothoid2D, inputPnt: Point3D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D clothoid

        Args:
            clothoid: 2D Clothoid
            inputPnt: Projection point as Point3D
            eps:      Tolerance

        Returns:
             Local point on the 2D clothoid,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(spline: Spline2D, inputPnt: Point2D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D spline

        emarks The old functions (splin7, splin2) can't process points which have no perpendicular point on the spline

        Args:
            spline:   2D Spline
            inputPnt: Projection point as Point2D
            eps:      Tolerance

        Returns:
             Local point on the 2D spline,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(spline: Spline2D, inputPnt: Point3D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D spline

        emarks The old functions (splin7, splin2) can't process points which have no perpendicular point on the spline

        Args:
            spline:   2D Spline
            inputPnt: Projection point as Point3D
            eps:      Tolerance

        Returns:
             Local point on the 2D spline,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(spline: Spline3D, inputPnt: Point2D, eps: float) -> tuple:
        """Calculate the local coordinates on a 3D spline

        emarks The old functions (splin7, splin2) can't process points which have no perpendicular point on the spline

        Args:
            spline:   3D Spline
            inputPnt: Projection point as Point2D
            eps:      Tolerance

        Returns:
             Local point on the 3D spline,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(spline: Spline3D, inputPnt: Point3D, eps: float) -> tuple:
        """Calculate the local coordinates on a 3D spline

        emarks The old functions (splin7, splin2) can't process points which have no perpendicular point on the spline

        Args:
            spline:   3D Spline
            inputPnt: Projection point as Point3D
            eps:      Tolerance

        Returns:
             Local point on the 3D spline,
            true if the calculation was successful
        """
    @staticmethod
    @typing.overload
    def PointLocal(geoObject: object, inputPnt: Point3D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D geometry object.

        Args:
            geoObject: First IGeometry object
            inputPnt:  Projection point
            eps:       Tolerance for clothoids and splines

        Returns:
             Local point on the geometry,
            true if the calculation was successful
        """
    def PointLocal(self):
        """ Overloaded function. See individual overloads.
        """
    @staticmethod
    def PointLocalEx(clothoid: Clothoid2D, inputPnt: Point2D, eps: float) -> tuple:
        """Calculate the local coordinates on a 2D clothoid

        PointLocalEx compute local point related to axis of clothoid (clothoid with parallel=0).
        This method is faster and computing X coordinate with higher precision.

        Use PointGlobalEx with PointLocalEx cooperation only.

        PointGlobalEx, TransformClothoidLocalOffset

        Args:
            clothoid: 2D Clothoid
            inputPnt: Projection point as Point2D
            eps:      Tolerance

        Returns:
             Axis local point on the 2D clothoid,
            true if the calculation was successful
        """
    @staticmethod
    def TransformClothoidLocalOffset(clothoid: Clothoid2D, offset: float, toAxis: bool) -> float:
        """Transform local offset between clothoid axis curve and parallel curve

        This function provides transformation between offset related to axis or parallel(real) curve.
        This function is useful when you have offset on parallel curve and want to get length of axis curve.
        If clothoid parameter Parallel is zero, then axis and parallel offsets are equal.

        Sample: calc real length of clothoid
        ndouble real_length = Service::Length(clot);
        double curve_length = TransformClothoidLocalOffset(clot, clot.Getlength(), false);

        real_length and curve_length are equal.

        Args:
            clothoid: 2D Clothoid
            offset:   Source offset
            toAxis:   If true, then  offset is offset on parallel curve and result will be offset on axis curve.

        Returns:
            Offset on axis or parallel curve, dependent on  toAxis.
        """

class Vector2D():
    """Representation class for 2D Vector.
    """
    def CrossProduct(self, vec: Vector2D) -> Vector3D:
        """Cross(vector) product operator.

        Formula: Va = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def DotProduct(self, vec: Vector2D) -> float:
        """Dot(sxcalar) product.

        Formula: S = Va . Vb = Va1 * Va2 + Vb1 * Vb2
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            double.
        """
    def GetAngle(self) -> Angle:
        """Get vector angle.

        Returns:
            Angle in a range <0, 2*PI> (normalized 2pi).
        """
    def GetAngleSigned(self) -> Angle:
        """Get vector angle.

        equivalent to zfno()

        Returns:
            Angle in a range <-PI..0..PI>
        """
    def GetCoords(self) -> tuple[float, float]:
        """Get copy of X, Y coordinates.

        Returns:
            tuple(X coordinate of vector,
                  Y coordinate of vector)
        """
    def GetLength(self) -> float:
        """Get vector length.

        Formula: Result(double) = ||Va||
        Va is this vector

        Returns:
            double.
        """
    def IsZero(self) -> bool:
        """Check the coords [0.0, 0.0] (binary comparison)

        Returns:
            Is zero? true/false
        """
    @typing.overload
    def Normalize(self):
        """Normalize vector.

        Formula: Vn(a1/||Va||, a2/||Va||)
        Va is this vector
        This method is checked and throwing a geometry exception when vector is zero.
        """
    @typing.overload
    def Normalize(self, length: float):
        """Normalize vector to new length.

        Formula: Vn(a1 * length / ||Va||, a2 * length / ||Va||)
        Va is this vector
        This method is checked and throwing a geometry exception when vector is zero.

        Args:
            length: new length of vector.
        """
    def Normalize(self):
        """ Overloaded function. See individual overloads.
        """
    def Orthogonal(self, counterClockwise: bool = True) -> Vector2D:
        """Compute orthogonal vector

        Method calculate orthogonal vector.
        Sample:

        vec = Vector2D(100., 0)
        vec.Orthogonal()
        # vec = (0., 100.);

        Args:
            counterClockwise: Orientation of orthogonal vector

        Returns:
            Orthogonal vector
        """
    def Reverse(self) -> Vector2D:
        """Compute reversed vector

        Method calculate vector with reversed orientation.

        Returns:
            Reversed vector
        """
    @typing.overload
    def Set(self, vec: Vector2D):
        """Initialize from vector 2D.

        Args:
            vec: Vector.
        """
    @typing.overload
    def Set(self, x: float, y: float):
        """Initialize from x,y coordinates.

        Args:
            x: coordinate.
            y: coordinate.
        """
    @typing.overload
    def Set(self, startPoint: Point2D, endPoint: Point2D):
        """Initialize vector from two points.

        Args:
            startPoint: start point of vector.
            endPoint:   end point of vector.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def Values(self) -> list[float]:
        """Get copy of X,Y coordinates as python list

        Returns:
            X coordinate of vector.,
            Y coordinate of vector.
        """
    def __add__(self, vec: Vector2D) -> Vector2D:
        """Addition operator.

        Formula: Vc = Va + Vb
        Va is this Vector.

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def __eq__(self, vec: Vector2D) -> bool:
        """Comparison of vectors without tolerance.

        Be careful, this method work without tolerance!

        Args:
            vec: Compared vector.

        Returns:
            True when points are equal, otherwise false.
        """
    def __iadd__(self, vec: Vector2D) -> Vector2D:
        """Addition assignment operator.

        Formula: Va = Va + Vb
        Va is this Vector.

        Args:
            vec: Vb Vector.

        Returns:
            Reference to vector.
        """
    def __idiv__(self, divider: float) -> Vector2D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            divider: scaling divider

        Returns:
            New vector
        """
    @typing.overload
    def __imul__(self, matrix: Matrix2D) -> Vector2D:
        """Matrix transformation.

        Formula: Vector(this) = Vector(this) * matrix

        Args:
            matrix: Transformation matrix.

        Returns:
            Vector2D.
        """
    @typing.overload
    def __imul__(self, factor: float) -> Vector2D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            factor: Scale factor

        Returns:
            New vector
        """
    def __imul__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, vec: Vector2D):
        """Copy constructor.

        Args:
            vec: Vector which will be copied.
        """
    @typing.overload
    def __init__(self, angle: Angle, length: float):
        """Constructor.

        Create vector from the angle and from the length.
        Formula: [X_COORD, Y_COORD] = [length*cos(angle), length*sin(angle)]

        Args:
            angle:  base angle.
            length: length of vector (must be greater then zero).
        """
    @typing.overload
    def __init__(self, x: float, y: float):
        """Constructor.

        Initialize vector from single coordinates.

        Args:
            x: X coordinate of vector.
            y: Y coordinate of vector.
        """
    @typing.overload
    def __init__(self, startPoint: Point2D, endPoint: Point2D):
        """Constructor.

        Initialize vector from two points.

        Args:
            startPoint: start point of vector.
            endPoint:   end point of vector.
        """
    @typing.overload
    def __init__(self, endPoint: Point2D):
        """Create a vector from a 2D point

        Args:
            endPoint: End point of the vector (startpoint is 0./0.)
        """
    @typing.overload
    def __init__(self, vec: Vector3D):
        """Copy constructor.

        Copy only X_COORD and Y_COORD from vector.

        Args:
            vec: 2D vector which will be copied to the 3D vector.
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, vec: Vector2D) -> Vector2D:
        """Subtraction assignment operator.

        Formula: Va = Va - Vb
        Va is this Vector.

        Args:
            vec: Vb Vector.

        Returns:
            Reference to vector.
        """
    @typing.overload
    def __mul__(self, vec: Vector2D) -> Vector3D:
        """Cross(vector) product operator.

        Formula: Vc = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> Vector2D:
        """Matrix transformation.

        Formula: Result = Vector(this) * matrix

        Args:
            matrix: Transformation matrix.

        Returns:
            Vector2D.
        """
    @typing.overload
    def __mul__(self, factor: float) -> Vector2D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            factor: Scale factor

        Returns:
            New vector
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, vec: Vector2D) -> bool:
        """Comparison of vectors without tolerance.

        Be careful, this method work without tolerance!

        Args:
            vec: Compared vector.

        Returns:
            True when points are not equal, otherwise false.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    def __sub__(self, vec: Vector2D) -> Vector2D:
        """Subtraction operator.

        Formula: Vc = Va - Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def __truediv__(self, divider: float) -> Vector2D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            divider: scaling divider

        Returns:
            New vector
        """
    @property
    def To3D(self) -> Vector3D:
        """convert to 3D3
        """
    @To3D.setter
    def To3D(self, value: Vector3D) -> None:
        """convert to 3D3
        """
    @property
    def X(self) -> float:
        """Get the X coordinate reference.
        """
    @X.setter
    def X(self, value: float) -> None:
        """Set  the X coordinate reference.
        """
    @property
    def Y(self) -> float:
        """Get the Y coordinate reference.
        """
    @Y.setter
    def Y(self, value: float) -> None:
        """Set  the Y coordinate reference.
        """

class Vector2DList():
    """List for Vector2D objects
    """
    def __contains__(self, value: Vector2D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Vector2D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Vector2DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Vector2D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Vector2DList:
        """Add a list

        Args:
            eleList: Vector2D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Vector2D):
        """Constructor with a Vector2D

        Args:
            ele: Vector2D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Vector2D

        Args:
            eleList: Vector2D list
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
    def __setitem__(self, index: (int | slice), value: Vector2D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Vector2D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Vector2DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Vector2D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class Vector3D():
    """Representation class for 3D Vector.
    """
    def CrossProduct(self, vec: Vector3D):
        """Cross(vector) product operator.

        Formula: Va = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).
        """
    def DotProduct(self, vec: Vector3D) -> float:
        """Dot(sxcalar) product.

        Formula: S = Va . Vb = Va1 * Va2 + Vb1 * Vb2
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            double.
        """
    def GetCoords(self) -> tuple[float, float, float]:
        """Get copy of X,Y,Z coordinates

        Returns:
            tuple(X coordinate of vector,
                  Y coordinate of vector,
                  Z coordinate of vector)
        """
    def GetLength(self) -> float:
        """Get vector length.

        Formula: Result(double) = ||Va||
        Va is this vector

        Returns:
            double.
        """
    def GetLengthSquare(self) -> float:
        """Get vector length without square-root in calculation.

        Returns:
            double.
        """
    def IsZero(self) -> bool:
        """Check the coords [0.0, 0.0, 0.0]

        If the coords are zero, the return value is true.
        If the coords aren't zero, the return value is false.

        Returns:
            Is zero? true/false
        """
    def Normal(self, vec: Vector3D) -> Vector3D:
        """Does the same as Cross(vector) product but does not change the operands.

        Formula: Vc = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).
        """
    @typing.overload
    def Normalize(self) -> eGeometryErrorCode:
        """Normalize vector.

        Formula: Vn(a1/||Va||, a2/||Va||)
        Va is this vector
        This method is checked and throwing a geometry exception when vector is zero.

        Returns:
            Geometry error code
        """
    @typing.overload
    def Normalize(self, length: float) -> eGeometryErrorCode:
        """Normalize vector to new length.

        Formula: Vn(a1 * length / ||Va||, a2 * length / ||Va||)
        Va is this vector
        This method is checked and throwing a geometry exception when vector is zero.

        Args:
            length: new length of vector.

        Returns:
            Geometry error code
        """
    def Normalize(self):
        """ Overloaded function. See individual overloads.
        """
    def Project(self, vec: Vector3D) -> Vector3D:
        """Projection operator.

        Formula: Vc = <Vb,Va>/<Va,Va> . Va
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def Reverse(self) -> Vector3D:
        """Compute reversed vector

        Method calculate vector with reversed orientation.

        Returns:
            Reversed vector
        """
    @typing.overload
    def Set(self, vec: Vector3D):
        """Initialize from vector 3D.

        Args:
            vec: Vector.
        """
    @typing.overload
    def Set(self, x: float, y: float, z: float):
        """Initialize from x,y,z coordinates.

        Args:
            x: coordinate.
            y: coordinate.
            z: coordinate.
        """
    @typing.overload
    def Set(self, startPoint: Point3D, endPoint: Point3D):
        """Initialize vector from two points.

        Args:
            startPoint: start point of vector.
            endPoint:   end point of vector.
        """
    def Set(self):
        """ Overloaded function. See individual overloads.
        """
    def Values(self) -> list[float]:
        """Get copy of X,Y,Z coordinates as python list

        Returns:
            X coordinate of vector.,
            Y coordinate of vector.,
            Z coordinate of vector.
        """
    def __add__(self, vec: Vector3D) -> Vector3D:
        """Addition operator.

        Formula: Vc = Va + Vb
        Va is this Vector.

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def __eq__(self, vec: Vector3D) -> bool:
        """Comparison of vectors without tolerance.

        Be careful, this method work without tolerance!

        Args:
            vec: Compared vector.

        Returns:
            True when points are equal, otherwise false.
        """
    def __iadd__(self, vec: Vector3D) -> Vector3D:
        """Addition assignment operator.

        Formula: Va = Va + Vb
        Va is this Vector.

        Args:
            vec: Vb Vector.

        Returns:
            Reference to vector.
        """
    def __idiv__(self, divider: float) -> Vector3D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            divider: scaling divider

        Returns:
            New vector
        """
    @typing.overload
    def __imul__(self, vec: Vector3D) -> Vector3D:
        """Cross(vector) product operator.

        Formula: Va = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            Reference to the cross(vector) product of vectors.
        """
    @typing.overload
    def __imul__(self, factor: float) -> Vector3D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            factor: Scale factor

        Returns:
            New vector
        """
    @typing.overload
    def __imul__(self, matrix: Matrix2D) -> Vector3D:
        """2D matrix transformation.

        Formula: Vector(this) = Vector(this) * matrix

        Args:
            matrix: 2D transformation matrix.

        Returns:
            Point.
        """
    @typing.overload
    def __imul__(self, matrix: Matrix3D) -> Vector3D:
        """3D matrix transformation.

        Formula: Vector(this) = Vector(this) * matrix

        Args:
            matrix: 3D transformation matrix.

        Returns:
            Point.
        """
    def __imul__(self):
        """ Overloaded function. See individual overloads.
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, vec: Vector2D):
        """Copy constructor.

        Copy only X_COORD and Y_COORD from vector, Z_COORD is set to zero.

        Args:
            vec: 2D vector which will be copied to the 3D vector.
        """
    @typing.overload
    def __init__(self, vec: Vector3D):
        """Copy constructor.

        Args:
            vec: vector which will be copied.
        """
    @typing.overload
    def __init__(self, x: float, y: float, z: float):
        """Constructor.

        Initialize vector from single coordinates.

        Args:
            x: X coordinate of vector.
            y: Y coordinate of vector.
            z: Z coordinate of vector.
        """
    @typing.overload
    def __init__(self, startPoint: Point3D, endPoint: Point3D):
        """Constructor.

        Initialize vector from two points.

        Args:
            startPoint: start point of vector.
            endPoint:   end point of vector.
        """
    @typing.overload
    def __init__(self, endPoint: Point3D):
        """Create a vector from a 3D point

        Args:
            endPoint: End point of the vector (startpoint is 0./0./0.)
        """
    def __init__(self):
        """ Overloaded function. See individual overloads.
        """
    def __isub__(self, vec: Vector3D) -> Vector3D:
        """Subtraction assignment operator.

        Formula: Va = Va - Vb
        Va is this Vector.

        Args:
            vec: Vb Vector.

        Returns:
            Reference to vector.
        """
    @typing.overload
    def __mul__(self, vec: Vector3D) -> Vector3D:
        """Cross(vector) product operator.

        Formula: Vc = Va x Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    @typing.overload
    def __mul__(self, factor: float) -> Vector3D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            factor: Scale factor

        Returns:
            New vector
        """
    @typing.overload
    def __mul__(self, matrix: Matrix2D) -> Vector3D:
        """2D matrix transformation.

        Formula: Result = Vector(this) * matrix

        Args:
            matrix: 2D transformation matrix.

        Returns:
            Point.
        """
    @typing.overload
    def __mul__(self, matrix: Matrix3D) -> Vector3D:
        """3D matrix transformation.

        Formula: Result = Vector(this) * matrix

        Args:
            matrix: 3D transformation matrix.

        Returns:
            Point.
        """
    def __mul__(self):
        """ Overloaded function. See individual overloads.
        """
    def __ne__(self, vec: Vector3D) -> bool:
        """Comparison of vectors without tolerance.

        Be careful, this method work without tolerance!

        Args:
            vec: Compared vector.

        Returns:
            True when points are not equal, otherwise false.
        """
    def __repr__(self) -> str:
        """Convert to string
        """
    def __sub__(self, vec: Vector3D) -> Vector3D:
        """Subtraction operator.

        Formula: Vc = Va - Vb
        Va is this Vector

        Args:
            vec: Vector(Vb).

        Returns:
            new Vector(Vc).
        """
    def __truediv__(self, divider: float) -> Vector3D:
        """Multiply the vector by a factor (scalar multiplication)

        Args:
            divider: scaling divider

        Returns:
            New vector
        """
    @property
    def To2D(self) -> Vector2D:
        """convert to 2D3
        """
    @To2D.setter
    def To2D(self, value: Vector2D) -> None:
        """convert to 2D3
        """
    @property
    def X(self) -> float:
        """Get the X coordinate reference.
        """
    @X.setter
    def X(self, value: float) -> None:
        """Set  the X coordinate reference.
        """
    @property
    def Y(self) -> float:
        """Get the Y coordinate reference.
        """
    @Y.setter
    def Y(self, value: float) -> None:
        """Set  the Y coordinate reference.
        """
    @property
    def Z(self) -> float:
        """Get the Z coordinate reference.
        """
    @Z.setter
    def Z(self, value: float) -> None:
        """Set  the Z coordinate reference.
        """

class Vector3DList():
    """List for Vector3D objects
    """
    def __contains__(self, value: Vector3D) -> bool:
        """Check for a value in the list

        Args:
            value: Value to check

        Returns:
            State for value is in the list
        """
    def __delitem__(self, value: Vector3D):
        """Delete a list item

        Args:
            value: Value to delete
        """
    def __eq__(self, compare_list: Vector3DList) -> bool:
        """Compare two lists

        Args:
            compare_list: List to compare

        Returns:
            Lists are equal state
        """
    def __getitem__(self, index: int) -> Vector3D:
        """Get a list item

        Args:
            index: Index of the item

        Returns:
            Value for the index
        """
    def __iadd__(self, eleList: list) -> Vector3DList:
        """Add a list

        Args:
            eleList: Vector3D list

        Returns:
            Lists with the added elements
        """
    @typing.overload
    def __init__(self):
        """Initialize
        """
    @typing.overload
    def __init__(self, ele: Vector3D):
        """Constructor with a Vector3D

        Args:
            ele: Vector3D
        """
    @typing.overload
    def __init__(self, eleList: list):
        """Constructor with a list of Vector3D

        Args:
            eleList: Vector3D list
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
    def __setitem__(self, index: (int | slice), value: Vector3D):
        """Set a list item

        Args:
            index: Index of the item
            value: Value to item
        """
    def append(self, value: Vector3D):
        """Append a list item

        Args:
            value: Value to append
        """
    @typing.overload
    def extend(self, iterable: Vector3DList):
        """Add the items from an iterable to the end of the list

        Args:
            iterable: Iterable to add
        """
    @typing.overload
    def extend(self, eleList: list):
        """Extend the list

        Args:
            eleList: Vector3D list
        """
    def extend(self):
        """ Overloaded function. See individual overloads.
        """

class eApproximationSettingsType(enum.Enum):
    """Type of Approximation settings

      Used for identification of Approximation settings type.

    ASET_SEGMENTATION    : Segmentation type
    ASET_MAX_LENGTH      : Maximal edge length type
    ASET_MAX_DISTANCE    : Maximal distance from curve
    ASET_BREP_TESSELATION: Density type for BRep3D tesselation
    """
    ASET_BREP_TESSELATION = 3
    ASET_MAX_DISTANCE = 2
    ASET_MAX_LENGTH = 1
    ASET_SEGMENTATION = 0

    names = {ASET_SEGMENTATION: ASET_SEGMENTATION,
             ASET_MAX_LENGTH: ASET_MAX_LENGTH,
             ASET_MAX_DISTANCE: ASET_MAX_DISTANCE,
             ASET_BREP_TESSELATION: ASET_BREP_TESSELATION}

    values = {0: ASET_SEGMENTATION,
              1: ASET_MAX_LENGTH,
              2: ASET_MAX_DISTANCE,
              3: ASET_BREP_TESSELATION}

    def __getitem__(self, key: (str | int | float)) -> eApproximationSettingsType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eBoolOpResult(enum.Enum):
    """bool operation result

      Used for an identification of boolean operation's result

    eInside : inside other geometry
    eOutside: outside other geometry
    eClip   : partly inside other geometry
    """
    eClip = 2
    eInside = 0
    eOutside = 1

    names = {eInside: eInside,
             eOutside: eOutside,
             eClip: eClip}

    values = {0: eInside,
              1: eOutside,
              2: eClip}

    def __getitem__(self, key: (str | int | float)) -> eBoolOpResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eBoxPoint(enum.Enum):
    """Get world point of a dedicated location of the box

    eLeftBottom  : 4----8----3
    eRightBottom : |         |
    eRightTop    : 9    5    7
    eLeftTop     : |         |
    eCenter      : 1----6----2
    eMiddleBottom:
    eMiddleRight :
    eMiddleTop   :
    eMiddleLeft  :
    """
    eCenter = 5
    eLeftBottom = 1
    eLeftTop = 4
    eMiddleBottom = 6
    eMiddleLeft = 9
    eMiddleRight = 7
    eMiddleTop = 8
    eRightBottom = 2
    eRightTop = 3

    names = {eLeftBottom: eLeftBottom,
             eRightBottom: eRightBottom,
             eRightTop: eRightTop,
             eLeftTop: eLeftTop,
             eCenter: eCenter,
             eMiddleBottom: eMiddleBottom,
             eMiddleRight: eMiddleRight,
             eMiddleTop: eMiddleTop,
             eMiddleLeft: eMiddleLeft}

    values = {1: eLeftBottom,
              2: eRightBottom,
              3: eRightTop,
              4: eLeftTop,
              5: eCenter,
              6: eMiddleBottom,
              7: eMiddleRight,
              8: eMiddleTop,
              9: eMiddleLeft}

    def __getitem__(self, key: (str | int | float)) -> eBoxPoint:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eClothoidType(enum.Enum):
    """Clothoid type identification.

    eClothoid         :
    eParabolaQuadratic:
    eParabolaGeneral  :
    """
    eClothoid = 1
    eParabolaGeneral = 3
    eParabolaQuadratic = 2

    names = {eClothoid: eClothoid,
             eParabolaQuadratic: eParabolaQuadratic,
             eParabolaGeneral: eParabolaGeneral}

    values = {1: eClothoid,
              2: eParabolaQuadratic,
              3: eParabolaGeneral}

    def __getitem__(self, key: (str | int | float)) -> eClothoidType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eComparisionResult(enum.Enum):
    """comparision result

      Used for better identification of comparision functionality's result

    eParallel         : parallel
    eAntiParallel     : parallel but with different orientation
    eNotParallel      : not parallel
    eOnElement        : position on element
    eLeft             : position left from element
    eRight            : position right from element
    eAbove            : position above element
    eBelow            : position below element
    eEqualToStartPoint: position on start point
    eEqualToEndPoint  : position on end point
    eInside           : position inside polygon
    eOutside          : position outside polygon
    eCrossing         : mutual crossing of 2 elements
    eUnknown          : position can not be evaluated, unknown reason
    """
    eAbove = 6
    eAntiParallel = 1
    eBelow = 7
    eCrossing = 12
    eEqualToEndPoint = 9
    eEqualToStartPoint = 8
    eInside = 10
    eLeft = 4
    eNotParallel = 2
    eOnElement = 3
    eOutside = 11
    eParallel = 0
    eRight = 5
    eUnknown = 13

    names = {eParallel: eParallel,
             eAntiParallel: eAntiParallel,
             eNotParallel: eNotParallel,
             eOnElement: eOnElement,
             eLeft: eLeft,
             eRight: eRight,
             eAbove: eAbove,
             eBelow: eBelow,
             eEqualToStartPoint: eEqualToStartPoint,
             eEqualToEndPoint: eEqualToEndPoint,
             eInside: eInside,
             eOutside: eOutside,
             eCrossing: eCrossing,
             eUnknown: eUnknown}

    values = {0: eParallel,
              1: eAntiParallel,
              2: eNotParallel,
              3: eOnElement,
              4: eLeft,
              5: eRight,
              6: eAbove,
              7: eBelow,
              8: eEqualToStartPoint,
              9: eEqualToEndPoint,
              10: eInside,
              11: eOutside,
              12: eCrossing,
              13: eUnknown}

    def __getitem__(self, key: (str | int | float)) -> eComparisionResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eCoordIdentification(enum.Enum):
    """Coordinate identification

      Used for better identification of coordinate index in array of values.

    X_COORD: X coordinate identification
    Y_COORD: Y coordinate identification
    Z_COORD: Z coordinate identification
    """
    X_COORD = 0
    Y_COORD = 1
    Z_COORD = 2

    names = {X_COORD: X_COORD,
             Y_COORD: Y_COORD,
             Z_COORD: Z_COORD}

    values = {0: X_COORD,
              1: Y_COORD,
              2: Z_COORD}

    def __getitem__(self, key: (str | int | float)) -> eCoordIdentification:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eCreatePatchResult(enum.Enum):
    """error codes for planar surface creation

    eOK                       :
    eError                    :
    eCurvesNotClosed          :
    eCurvesAreSelfIntersecting:
    """
    eCurvesAreSelfIntersecting = 3
    eCurvesNotClosed = 2
    eError = 1
    eOK = 0

    names = {eOK: eOK,
             eError: eError,
             eCurvesNotClosed: eCurvesNotClosed,
             eCurvesAreSelfIntersecting: eCurvesAreSelfIntersecting}

    values = {0: eOK,
              1: eError,
              2: eCurvesNotClosed,
              3: eCurvesAreSelfIntersecting}

    def __getitem__(self, key: (str | int | float)) -> eCreatePatchResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eFilletErrorCode(enum.Enum):
    """Enumeration of error codes for Fillet

    eNO_ERROR                    : No error
    eERROR_LINES_ARENOT_COPLANAR : Lines aren't coplanar
    eERROR_LINES_ARE_COLLINEAR   : Lines are collinear
    eERROR_LINES_ARE_PARALLEL    : Lines are parallel
    eERROR_ZEROO_LINE_LENGTH     : Line has zero length
    eERROR_NO_FILLET_CREATED     : Fillet hasn't been created
    eERROR_LINES_ARE_NOT_PARALLEL: Lines are not parallel
    """
    eERROR_LINES_ARENOT_COPLANAR = 1
    eERROR_LINES_ARE_COLLINEAR = 2
    eERROR_LINES_ARE_NOT_PARALLEL = 6
    eERROR_LINES_ARE_PARALLEL = 3
    eERROR_NO_FILLET_CREATED = 5
    eERROR_ZEROO_LINE_LENGTH = 4
    eNO_ERROR = 0

    names = {eNO_ERROR: eNO_ERROR,
             eERROR_LINES_ARENOT_COPLANAR: eERROR_LINES_ARENOT_COPLANAR,
             eERROR_LINES_ARE_COLLINEAR: eERROR_LINES_ARE_COLLINEAR,
             eERROR_LINES_ARE_PARALLEL: eERROR_LINES_ARE_PARALLEL,
             eERROR_ZEROO_LINE_LENGTH: eERROR_ZEROO_LINE_LENGTH,
             eERROR_NO_FILLET_CREATED: eERROR_NO_FILLET_CREATED,
             eERROR_LINES_ARE_NOT_PARALLEL: eERROR_LINES_ARE_NOT_PARALLEL}

    values = {0: eNO_ERROR,
              1: eERROR_LINES_ARENOT_COPLANAR,
              2: eERROR_LINES_ARE_COLLINEAR,
              3: eERROR_LINES_ARE_PARALLEL,
              4: eERROR_ZEROO_LINE_LENGTH,
              5: eERROR_NO_FILLET_CREATED,
              6: eERROR_LINES_ARE_NOT_PARALLEL}

    def __getitem__(self, key: (str | int | float)) -> eFilletErrorCode:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eFilletType(enum.Enum):
    """Enumeration for the type of Fillet

    FT_UNKNOWN                     : Unknown fillet type
    FT_LL_INTERSECTION_ON_LINE     : Intersection of two lines is on line
    FT_LL_INTERSECTION_AT_THE_END  : Intersection of two lines is at the end of lines
    FT_LL_INTERSECTION_OUT_OF_LINES: Intersection of two lines is out of lines
    FT_LL_PARALLEL_LINES           : Intersection of two Lines are parallel
    FT_LC_TWO_INTERSECTION         : Intersection of line and circle - two intersections
    FT_LC_ONE_INTERSECTION         : Intersection of line and circle - one intersections
    FT_LC_NO_INTERSECTION          : Intersection of line and circle - no intersections
    FT_CC_TWO_INTERSECTION         : Intersection of two circles - two intersections
    FT_CC_ONE_INTERSECTION         : Intersection of two circles - one intersections
    FT_CC_NO_INTERSECTION          : Intersection of two circles - no intersections
    FT_CC_CONCETRIC                : Concentric lines - no intersections
    FT_KK_KURVE_ELEMENTS           : Intersection of two curve elements
    FT_KK_PARALLEL_KURVE_ELEMENTS  : Intersection of two parallel curve elements
    """
    FT_CC_CONCETRIC = 33
    FT_CC_NO_INTERSECTION = 32
    FT_CC_ONE_INTERSECTION = 31
    FT_CC_TWO_INTERSECTION = 30
    FT_KK_KURVE_ELEMENTS = 40
    FT_KK_PARALLEL_KURVE_ELEMENTS = 41
    FT_LC_NO_INTERSECTION = 22
    FT_LC_ONE_INTERSECTION = 21
    FT_LC_TWO_INTERSECTION = 20
    FT_LL_INTERSECTION_AT_THE_END = 11
    FT_LL_INTERSECTION_ON_LINE = 10
    FT_LL_INTERSECTION_OUT_OF_LINES = 12
    FT_LL_PARALLEL_LINES = 13
    FT_UNKNOWN = 0

    names = {FT_UNKNOWN: FT_UNKNOWN,
             FT_LL_INTERSECTION_ON_LINE: FT_LL_INTERSECTION_ON_LINE,
             FT_LL_INTERSECTION_AT_THE_END: FT_LL_INTERSECTION_AT_THE_END,
             FT_LL_INTERSECTION_OUT_OF_LINES: FT_LL_INTERSECTION_OUT_OF_LINES,
             FT_LL_PARALLEL_LINES: FT_LL_PARALLEL_LINES,
             FT_LC_TWO_INTERSECTION: FT_LC_TWO_INTERSECTION,
             FT_LC_ONE_INTERSECTION: FT_LC_ONE_INTERSECTION,
             FT_LC_NO_INTERSECTION: FT_LC_NO_INTERSECTION,
             FT_CC_TWO_INTERSECTION: FT_CC_TWO_INTERSECTION,
             FT_CC_ONE_INTERSECTION: FT_CC_ONE_INTERSECTION,
             FT_CC_NO_INTERSECTION: FT_CC_NO_INTERSECTION,
             FT_CC_CONCETRIC: FT_CC_CONCETRIC,
             FT_KK_KURVE_ELEMENTS: FT_KK_KURVE_ELEMENTS,
             FT_KK_PARALLEL_KURVE_ELEMENTS: FT_KK_PARALLEL_KURVE_ELEMENTS}

    values = {0: FT_UNKNOWN,
              10: FT_LL_INTERSECTION_ON_LINE,
              11: FT_LL_INTERSECTION_AT_THE_END,
              12: FT_LL_INTERSECTION_OUT_OF_LINES,
              13: FT_LL_PARALLEL_LINES,
              20: FT_LC_TWO_INTERSECTION,
              21: FT_LC_ONE_INTERSECTION,
              22: FT_LC_NO_INTERSECTION,
              30: FT_CC_TWO_INTERSECTION,
              31: FT_CC_ONE_INTERSECTION,
              32: FT_CC_NO_INTERSECTION,
              33: FT_CC_CONCETRIC,
              40: FT_KK_KURVE_ELEMENTS,
              41: FT_KK_PARALLEL_KURVE_ELEMENTS}

    def __getitem__(self, key: (str | int | float)) -> eFilletType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eGeometryErrorCode(enum.Enum):
    """Geometry error codes
    """
    eAllocError = 1234
    eError = 1
    eInvalid3DLine = 512
    eOK = 0
    eOutOfRange = 256
    eStructuralError = 4
    eWarpedPolygonalFace = 8
    eWrongShape = 2

    names = {eOK: eOK,
             eError: eError,
             eWrongShape: eWrongShape,
             eStructuralError: eStructuralError,
             eWarpedPolygonalFace: eWarpedPolygonalFace,
             eOutOfRange: eOutOfRange,
             eInvalid3DLine: eInvalid3DLine,
             eAllocError: eAllocError}

    values = {0: eOK,
              1: eError,
              2: eWrongShape,
              4: eStructuralError,
              8: eWarpedPolygonalFace,
              256: eOutOfRange,
              512: eInvalid3DLine,
              1234: eAllocError}

    def __getitem__(self, key: (str | int | float)) -> eGeometryErrorCode:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eHiddenCalculationResult(enum.Enum):
    """Result of hidden calculation for line.

    eVisible: Line is visible.
    eHidden : Line is invisible/hidden.
    """
    eHidden = 1
    eVisible = 0

    names = {eVisible: eVisible,
             eHidden: eHidden}

    values = {0: eVisible,
              1: eHidden}

    def __getitem__(self, key: (str | int | float)) -> eHiddenCalculationResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eLinePointIdentification(enum.Enum):
    """Start and end point identification

      Used for better identification of start and end point.

    START_POINT: Start point identification
    END_POINT  : End point identification
    """
    END_POINT = 1
    START_POINT = 0

    names = {START_POINT: START_POINT,
             END_POINT: END_POINT}

    values = {0: START_POINT,
              1: END_POINT}

    def __getitem__(self, key: (str | int | float)) -> eLinePointIdentification:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ePlanarSurfaceError(enum.Enum):
    """error codes for planar surface creation

    eCollinear    :
    eNotPlanar    :
    eNotContinuous:
    eError        :
    eOK           :
    """
    eCollinear = 0
    eError = 3
    eNotContinuous = 2
    eNotPlanar = 1
    eOK = 4

    names = {eCollinear: eCollinear,
             eNotPlanar: eNotPlanar,
             eNotContinuous: eNotContinuous,
             eError: eError,
             eOK: eOK}

    values = {0: eCollinear,
              1: eNotPlanar,
              2: eNotContinuous,
              3: eError,
              4: eOK}

    def __getitem__(self, key: (str | int | float)) -> ePlanarSurfaceError:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ePolygonHealingSettings(enum.Enum):
    """Type of Healing settings for polygon

      Used for identification of Healing settings type for polygon.

    PHSET_NOMODIFY : Default: no modification
    PHSET_NORMALIZE: use normalize
    """
    PHSET_NOMODIFY = 0
    PHSET_NORMALIZE = 1

    names = {PHSET_NOMODIFY: PHSET_NOMODIFY,
             PHSET_NORMALIZE: PHSET_NORMALIZE}

    values = {0: PHSET_NOMODIFY,
              1: PHSET_NORMALIZE}

    def __getitem__(self, key: (str | int | float)) -> ePolygonHealingSettings:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ePolygonNormalizeType(enum.Enum):
    """type of Polygon2D normalization

      map kenn0 to an enum, see kgNormPoly

    DEFAULT_NORM_TYPE        : without special effects
    SIDEFACE_NORM_TYPE       : side faces or Leisten included
    HATCHING_MEASUR_NORM_TYPE: 'hatching' only for measuring area
    HATCHING_NORM_TYPE       : 'hatching' for going on with work
    STARTPOINT_NORM_TYPE     : like 0 and additionally look for start point
    """
    DEFAULT_NORM_TYPE = 0
    HATCHING_MEASUR_NORM_TYPE = 2
    HATCHING_NORM_TYPE = 3
    SIDEFACE_NORM_TYPE = 1
    STARTPOINT_NORM_TYPE = 4

    names = {DEFAULT_NORM_TYPE: DEFAULT_NORM_TYPE,
             SIDEFACE_NORM_TYPE: SIDEFACE_NORM_TYPE,
             HATCHING_MEASUR_NORM_TYPE: HATCHING_MEASUR_NORM_TYPE,
             HATCHING_NORM_TYPE: HATCHING_NORM_TYPE,
             STARTPOINT_NORM_TYPE: STARTPOINT_NORM_TYPE}

    values = {0: DEFAULT_NORM_TYPE,
              1: SIDEFACE_NORM_TYPE,
              2: HATCHING_MEASUR_NORM_TYPE,
              3: HATCHING_NORM_TYPE,
              4: STARTPOINT_NORM_TYPE}

    def __getitem__(self, key: (str | int | float)) -> ePolygonNormalizeType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class ePolyhedronHealingSettings(enum.Enum):
    """Type of Healing settings for polyhedron

      Used for identification of Healing settings type for polyhedron.

    HSET_TRIANGULATE: default: Invalid faces will be triangulated
    HSET_TILT       : Face vertices will be tilted
    HSET_NOMODIFY   : no modification
    HSET_UNKNOWN    : unknown type
    """
    HSET_NOMODIFY = 2
    HSET_TILT = 1
    HSET_TRIANGULATE = 0
    HSET_UNKNOWN = 3

    names = {HSET_TRIANGULATE: HSET_TRIANGULATE,
             HSET_TILT: HSET_TILT,
             HSET_NOMODIFY: HSET_NOMODIFY,
             HSET_UNKNOWN: HSET_UNKNOWN}

    values = {0: HSET_TRIANGULATE,
              1: HSET_TILT,
              2: HSET_NOMODIFY,
              3: HSET_UNKNOWN}

    def __getitem__(self, key: (str | int | float)) -> ePolyhedronHealingSettings:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eProjectionMatrixType(enum.Enum):
    """Type of projection in Matrix3D

      Used for an identification of what kind of projection is in Matrix3D.

    LEFT_2D  : -3 ->  X
    RIGHT_2D : 3 -> -X
    FRONT_2D : -2 ->  Y
    REAR_2D  : 2 -> -Y
    TOP_2D   : 1 -> -Z
    BOTTOM_2D: -1 ->  Z
    FREE_3D  : Free projection
    """
    BOTTOM_2D = 5
    FREE_3D = 6
    FRONT_2D = 2
    LEFT_2D = 0
    REAR_2D = 3
    RIGHT_2D = 1
    TOP_2D = 4

    names = {LEFT_2D: LEFT_2D,
             RIGHT_2D: RIGHT_2D,
             FRONT_2D: FRONT_2D,
             REAR_2D: REAR_2D,
             TOP_2D: TOP_2D,
             BOTTOM_2D: BOTTOM_2D,
             FREE_3D: FREE_3D}

    values = {0: LEFT_2D,
              1: RIGHT_2D,
              2: FRONT_2D,
              3: REAR_2D,
              4: TOP_2D,
              5: BOTTOM_2D,
              6: FREE_3D}

    def __getitem__(self, key: (str | int | float)) -> eProjectionMatrixType:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eServiceResult(enum.Enum):
    """service result

      Used for an identification of service functionality result

    POSITIVE_ORIENTATION   : Orientation Counter-Clockwise
    NEGATIVE_ORIENTATION   : Orientation Clockwise
    NO_ERR                 : Error No error
    INVALID_LINE           : Error Invalid Line
    INVALID_POLYLINE       : Error Invalid Polyline
    INVALID_POLYGON        : Error Invalid Polygon
    INVALID_POLYHEDRON     : Error Invalid Polyhedron
    ZERO_ANGLE             : Error Zero Angle
    PARALLEL_LINES         : Lines are parallel
    INVALID_GEOOBJECT      : Error Invalid Geo Object
    INVALID_POINT          : Error Invalid Point
    INVALID_CUBOID         : Error Invalid Cuboid
    INVALID_CYLINDER       : Error Invalid Cylinder
    INVALID_CONE           : Error Invalid Cone
    INVALID_ELLIPSOID      : Error Invalid Ellipsoid
    INVALID_SURFACE        : Error Invalid Surface
    FAILED_TO_INVERT_MATRIX: Error Matix inversion failed
    FAILED_TO_CONVERGE     : Error method failed to converge
    INVALID_POINTCLOUD     : Error Invalid point cloud
    IS_ABOVE               : Geometry is ABOVE the element
    IS_BELOW               : Geometry is BELOW the element
    IS_IN                  : Geometry is in, not above, not below
    IS_UNKNOWN             : Geometry has not recognized position
    """
    FAILED_TO_CONVERGE = 17
    FAILED_TO_INVERT_MATRIX = 16
    INVALID_CONE = 13
    INVALID_CUBOID = 11
    INVALID_CYLINDER = 12
    INVALID_ELLIPSOID = 14
    INVALID_GEOOBJECT = 9
    INVALID_LINE = 3
    INVALID_POINT = 10
    INVALID_POINTCLOUD = 18
    INVALID_POLYGON = 5
    INVALID_POLYHEDRON = 6
    INVALID_POLYLINE = 4
    INVALID_SURFACE = 15
    IS_ABOVE = 19
    IS_BELOW = 20
    IS_IN = 21
    IS_UNKNOWN = 22
    NEGATIVE_ORIENTATION = 1
    NO_ERR = 2
    PARALLEL_LINES = 8
    POSITIVE_ORIENTATION = 0
    ZERO_ANGLE = 7

    names = {POSITIVE_ORIENTATION: POSITIVE_ORIENTATION,
             NEGATIVE_ORIENTATION: NEGATIVE_ORIENTATION,
             NO_ERR: NO_ERR,
             INVALID_LINE: INVALID_LINE,
             INVALID_POLYLINE: INVALID_POLYLINE,
             INVALID_POLYGON: INVALID_POLYGON,
             INVALID_POLYHEDRON: INVALID_POLYHEDRON,
             ZERO_ANGLE: ZERO_ANGLE,
             PARALLEL_LINES: PARALLEL_LINES,
             INVALID_GEOOBJECT: INVALID_GEOOBJECT,
             INVALID_POINT: INVALID_POINT,
             INVALID_CUBOID: INVALID_CUBOID,
             INVALID_CYLINDER: INVALID_CYLINDER,
             INVALID_CONE: INVALID_CONE,
             INVALID_ELLIPSOID: INVALID_ELLIPSOID,
             INVALID_SURFACE: INVALID_SURFACE,
             FAILED_TO_INVERT_MATRIX: FAILED_TO_INVERT_MATRIX,
             FAILED_TO_CONVERGE: FAILED_TO_CONVERGE,
             INVALID_POINTCLOUD: INVALID_POINTCLOUD,
             IS_ABOVE: IS_ABOVE,
             IS_BELOW: IS_BELOW,
             IS_IN: IS_IN,
             IS_UNKNOWN: IS_UNKNOWN}

    values = {0: POSITIVE_ORIENTATION,
              1: NEGATIVE_ORIENTATION,
              2: NO_ERR,
              3: INVALID_LINE,
              4: INVALID_POLYLINE,
              5: INVALID_POLYGON,
              6: INVALID_POLYHEDRON,
              7: ZERO_ANGLE,
              8: PARALLEL_LINES,
              9: INVALID_GEOOBJECT,
              10: INVALID_POINT,
              11: INVALID_CUBOID,
              12: INVALID_CYLINDER,
              13: INVALID_CONE,
              14: INVALID_ELLIPSOID,
              15: INVALID_SURFACE,
              16: FAILED_TO_INVERT_MATRIX,
              17: FAILED_TO_CONVERGE,
              18: INVALID_POINTCLOUD,
              19: IS_ABOVE,
              20: IS_BELOW,
              21: IS_IN,
              22: IS_UNKNOWN}

    def __getitem__(self, key: (str | int | float)) -> eServiceResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eSplitResult(enum.Enum):
    """result of split a geometry element

    eSplitNone           : No valid split found
    eSplitOk             : Geometry was split into at least two pieces
    eSplitInvalidGeometry: The input geometry is invalid
    eSplitInvalidArgs    : Not all input arguments are valid
    """
    eSplitInvalidArgs = 3
    eSplitInvalidGeometry = 2
    eSplitNone = 0
    eSplitOk = 1

    names = {eSplitNone: eSplitNone,
             eSplitOk: eSplitOk,
             eSplitInvalidGeometry: eSplitInvalidGeometry,
             eSplitInvalidArgs: eSplitInvalidArgs}

    values = {0: eSplitNone,
              1: eSplitOk,
              2: eSplitInvalidGeometry,
              3: eSplitInvalidArgs}

    def __getitem__(self, key: (str | int | float)) -> eSplitResult:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eSurfaceTrimParam(enum.Enum):
    """Trimming curve surface param for naturally trimmed surfaces

    eTrimUndefined       :
    eTrimUMinValue       : Edge is trimming the surface by its u-min value.
    eTrimUMinValueReverse: Edge is trimming the surface by its u-min value in reverse order.
    eTrimUMaxValue       : Edge is trimming the surface by its u-max value.
    eTrimUMaxValueReverse: Edge is trimming the surface by its u-max value in reverse order.
    eTrimVMinValue       : Edge is trimming the surface by its v-min value.
    eTrimVMinValueReverse: Edge is trimming the surface by its v-min value inreverse order.
    eTrimVMaxValue       : Edge is trimming the surface by its v-max value.
    eTrimVMaxValueReverse: Edge is trimming the surface by its v-max value in reverse order.
    """
    eTrimUMaxValue = 3
    eTrimUMaxValueReverse = 4
    eTrimUMinValue = 1
    eTrimUMinValueReverse = 2
    eTrimUndefined = 0
    eTrimVMaxValue = 7
    eTrimVMaxValueReverse = 8
    eTrimVMinValue = 5
    eTrimVMinValueReverse = 6

    names = {eTrimUndefined: eTrimUndefined,
             eTrimUMinValue: eTrimUMinValue,
             eTrimUMinValueReverse: eTrimUMinValueReverse,
             eTrimUMaxValue: eTrimUMaxValue,
             eTrimUMaxValueReverse: eTrimUMaxValueReverse,
             eTrimVMinValue: eTrimVMinValue,
             eTrimVMinValueReverse: eTrimVMinValueReverse,
             eTrimVMaxValue: eTrimVMaxValue,
             eTrimVMaxValueReverse: eTrimVMaxValueReverse}

    values = {0: eTrimUndefined,
              1: eTrimUMinValue,
              2: eTrimUMinValueReverse,
              3: eTrimUMaxValue,
              4: eTrimUMaxValueReverse,
              5: eTrimVMinValue,
              6: eTrimVMinValueReverse,
              7: eTrimVMaxValue,
              8: eTrimVMaxValueReverse}

    def __getitem__(self, key: (str | int | float)) -> eSurfaceTrimParam:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


class eValidationStatusPolygon3D(enum.Enum):
    """Polygon validation status

    VS_COLINEAR    : The points of the polygon are on the same line
    VS_NOT_COPLANAR: The points of the polygon are not on the same plane
    """
    VS_COLINEAR = 0
    VS_NOT_COPLANAR = 1

    names = {VS_COLINEAR: VS_COLINEAR,
             VS_NOT_COPLANAR: VS_NOT_COPLANAR}

    values = {0: VS_COLINEAR,
              1: VS_NOT_COPLANAR}

    def __getitem__(self, key: (str | int | float)) -> eValidationStatusPolygon3D:
        """ get the item for a key

        Args:
            key: value key

        Returns:
            value for the key
        """
        return self.values[key]


@typing.overload
def AddToMinMax(minMax: MinMax2D, point: Point2D):
    """Calculate 2D-Min- and Max Point of an 2D point

    Calculates the MinMax2D volume by the Point2D given in parameter point.

    Args:
        minMax: where to ad min max box
        point:  Point2D to be added
    """
@typing.overload
def AddToMinMax(minMax: MinMax2D, point: Point3D):
    """Calculate 2D-Min- and Max Point of an 3D point

    Calculates the MinMax2D volume by the Point3D given in parameter point.

    Args:
        minMax: where to ad min max box
        point:  Point3D to be added
    """
@typing.overload
def AddToMinMax(minMax: MinMax3D, point: Point3D):
    """Calculate 3D-Min- and Max Point of an 3D point

    Calculates the MinMax3D volume by the Point3D given in parameter point.

    Args:
        minMax: where to ad min max box
        point:  Point3D to be added
    """
@typing.overload
def AddToMinMax(minMax: MinMax3D, point: Point2D):
    """Calculate 3D-Min- and Max Point of an 2D point

    Calculates the MinMax3D volume by the Point2D given in parameter point.

    Args:
        minMax: where to ad min max box
        point:  Point2D to be added
    """
def AddToMinMax(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CalcAngle(l1: Line2D) -> tuple:
    """compute angle of 2D line and x axis

    Args:
        l1: 2D Line

    Returns:
        result angle (normalized 2pi),
        NO_ERR, INVALID_LINE (lines is degenerated)
    """
@typing.overload
def CalcAngle(point1: Point2D, point2: Point2D) -> Angle:
    """compute angle of 2D points

    Args:
        point1: 1st point
        point2: 2nd point

    Returns:
        result angle (normalized 2pi)
    """
def CalcAngle(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CalcArea(p1: Point2D, p2: Point2D, p3: Point2D) -> tuple:
    """compute area of a triangle

    Args:
        p1: 1. Point
        p2: 2. Point
        p3: 3. Point

    Returns:
        area result area,
        POSITIVE_ORIENTATION, NEGATIVE_ORIENTATION
    """
@typing.overload
def CalcArea(polygon: Polygon2D) -> tuple:
    """Get the area of a 2D Polygon
    NEGATIVE_ORIENTATION for a CW orientated polygon, INVALID_POLYGON on error

    If an instance denotes an incorrect polygon (e.g. not enough points), the method will return INVALID_POLYGON.
    us, one can distinguish between a collapsed polygon with area = 0.0 and a wrong shape.
    The polygon must not be self-intersecting. In case of self intersection the area result is currently
    defined and the return value indicates no error.
     interface: age

    Args:
        polygon: The polygon those area is requested

    Returns:
        The area of the polygon,
        The eServiceResult of the operation, POSITIVE_ORIENTATION for a CCW orientated polygon,
        NEGATIVE_ORIENTATION for a CW orientated polygon, INVALID_POLYGON on error
    """
@typing.overload
def CalcArea(polygon: Polygon3D) -> tuple:
    """Get the area of a Polygon3D

    Args:
        polygon: polygon to measure

    Returns:
        area of the polygon,
        eServiceResult of the operation, POSITIVE_ORIENTATION or INVALID_POLYGON on error
    """
@typing.overload
def CalcArea(polygonalArea: PolygonalArea3D) -> tuple:
    """Get the area of a PolygonalArea

    or INVALID_POLYGON on error
    e: berechnePolygonFlaeche

    Args:
        polygonalArea

    Returns:
        The area of the PolygonalArea,
        The eServiceResult of the operation, POSITIVE_ORIENTATION
        or INVALID_POLYGON on error
        Old interface: berechnePolygonFlaeche

            -----------------------------------------------------------------------------
    """
@typing.overload
def CalcArea(areaGeo: ClosedArea2D, arcSegmentation: int, useArcSegmentation: int, armLength: float, riseValue: float) -> tuple:
    """Get the area of a 2D path bounded closed area
    NEGATIVE_ORIENTATION for a CW orientated area boundary, INVALID_POLYGON on error

    Args:
        areaGeo:            The path bounded closed area those area is requested
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline

    Returns:
        The area of the given geometry,
        The eServiceResult of the operation, POSITIVE_ORIENTATION for a CCW orientated area boundary,
        NEGATIVE_ORIENTATION for a CW orientated area boundary, INVALID_POLYGON on error
    """
@typing.overload
def CalcArea(areaGeo: ClosedAreaComposite2D, arcSegmentation: int, useArcSegmentation: int, armLength: float,
             riseValue: float) -> tuple:
    """Get the area of a 2D path bounded closed area composite
    NEGATIVE_ORIENTATION for a CW orientated area boundary, INVALID_POLYGON on error

    Args:
        areaGeo:            The path bounded closed area composite those area is requested
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline

    Returns:
        The area of the given geometry,
        The eServiceResult of the operation, POSITIVE_ORIENTATION for a CCW orientated area boundary,
        NEGATIVE_ORIENTATION for a CW orientated area boundary, INVALID_POLYGON on error
    """
def CalcArea(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CalcLength(el: Line2D) -> float:
    """calculate length of a 2D line.

    Args:
        el: 2D line.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(vec: Vector2D) -> float:
    """calculate length of a 2D vector.

    Args:
        vec: 2D vector.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(polyline: Polyline2D) -> float:
    """Calculate the Length of a 2D Polyline.

    Args:
        polyline: 2D Polyline

    Returns:
        Length of the given polyline.
    """
@typing.overload
def CalcLength(polygon: Polygon2D) -> float:
    """Calculate the Length of a 2D Polygon.

    Result is length from all components, doesn't matter if it's solid or hole.

    Args:
        polygon: 2D Polygon

    Returns:
        Length of the given polygon.
    """
@typing.overload
def CalcLength(polygon: Polygon3D) -> float:
    """Calculate the Length of a 3D Polygon.

    Result is length from all components, doesn't matter if it's solid or hole.

    Args:
        polygon: 3D Polygon

    Returns:
        Length of the given polygon.
    """
@typing.overload
def CalcLength(arc: Arc2D) -> float:
    """Calculate the Length of a 2D arc.

    Args:
        arc: 2D Arc

    Returns:
        Length of the given arc.
    """
@typing.overload
def CalcLength(clothoid: Clothoid2D) -> float:
    """Calculate the Length of a 2D clothoid.

    Args:
        clothoid: 2D Clothoid

    Returns:
        Length of the given clothoid.
    """
@typing.overload
def CalcLength(spline: Spline2D) -> float:
    """Calculate the Length of a 2D spline.

    Args:
        spline: 2D Spline

    Returns:
        Length of the given spline.
    """
@typing.overload
def CalcLength(path: Path2D) -> float:
    """Calculate the Length of a Path 2D.

    Args:
        path: Path2D

    Returns:
        Length of the given Path2D
    """
@typing.overload
def CalcLength(line: Line3D) -> float:
    """calculate length of a 3D line.

    Args:
        line: 3D line.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(vec: Vector3D) -> float:
    """calculate length of a 3D vector.

    Args:
        vec: 3D vector.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(polyline: Polyline3D) -> float:
    """calculate length of a 3D polyline.

    Args:
        polyline: 3D polyline.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(arc: Arc3D) -> float:
    """calculate length of a 3D Arc.

    Args:
        arc: 3D arc.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(path: Path3D) -> float:
    """calculate length of a 3D path.

    Args:
        path: 3D path.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(poly: Polyhedron3D) -> float:
    """calculate length of a polyhedron of edge type.

    Args:
        poly: Polyhedron3D.

    Returns:
        double result.
    """
@typing.overload
def CalcLength(spline: Spline3D) -> float:
    """Calculate the Length of a 3D spline.

    Args:
        spline: 3D Spline

    Returns:
        Length of the given spline.
    """
@typing.overload
def CalcLength(spline: Spline3D) -> float:
    """Calculate the Length of a 3D spline.

    Args:
        spline: 3D Spline

    Returns:
        Length of the given spline.
    """
@typing.overload
def CalcLength(spline: BSpline3D) -> float:
    """Calculate the Length of a 3D bspline.

    Args:
        spline: 3D BSpline

    Returns:
        Length of the given spline.
    """
def CalcLength(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CalcMass(elem: Polyhedron3D) -> tuple:
    """Calculate mass values

    Args:
        elem: Polyhedron3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: Cuboid3D) -> tuple:
    """Calculate mass values

    Args:
        elem: Cuboid3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: Cylinder3D) -> tuple:
    """Calculate mass values

    Args:
        elem: Cylinder3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: Ellipsoid3D) -> tuple:
    """Calculate mass values

    Args:
        elem: Ellipsoid3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: Cone3D) -> tuple:
    """Calculate mass values

    Args:
        elem: Cone3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: ClippedSweptSolid3D) -> tuple:
    """Calculate mass values

    Args:
        elem: ClippedSweptSolid3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: ExtrudedAreaSolid3D) -> tuple:
    """Calculate mass values

    Args:
        elem: ExtrudedAreaSolid3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
@typing.overload
def CalcMass(elem: BRep3D) -> tuple:
    """Calculate mass values

    Args:
        elem: BRep3D

    Returns:
         error code,
        calculated volume,
        calculated surface,
        calculated gravity point
    """
def CalcMass(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CalcMinMax(point: Point2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Point2D given in parameter point

    Args:
        point: Point2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(line: Line2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Line2D given in parameter line.

    Args:
        line: Line2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(polyline: Polyline2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Polyline2D given in parameter polyline.

    Args:
        polyline: Polyline2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR, INVALID_POLYLINE)
    """
@typing.overload
def CalcMinMax(polygon: Polygon2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Polygon2D given in parameter polygon.

    Args:
        polygon: Polygon2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR, INVALID_POLYGON)
    """
@typing.overload
def CalcMinMax(arc: Arc2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Arc2D given in parameter arc.

    Args:
        arc: Arc2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(spline: Spline2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Spline2D given in parameter spline.

    Args:
        spline: Spline2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(spline: Spline3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax3D box of the Spline3D given in parameter spline.

    Args:
        spline: Spline3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(spline: BSpline3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax3D box of the BSpline3D given in parameter spline.

    Args:
        spline: BSpline3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(spline: BSpline2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box of the BSpline2D given in parameter spline.

    Args:
        spline: BSpline2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(clothoid: Clothoid2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box by the Clothoid2D given in parameter clothoid.

    Args:
        clothoid: Clothoid to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(path: Path2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box of the Path2D.

    Args:
        path: Path2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(area: ClosedArea2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box of the ClosedArea2D.

    Args:
        area: ClosedArea2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(area: ClosedAreaComposite2D) -> tuple[MinMax2D, eServiceResult]:
    """Calculate Min- and Max Point of an element.

    Calculates the MinMax2D box of the ClosedAreaComposite2D.

    Args:
        area: ClosedAreaComposite2D to be calculated

    Returns:
        tuple(MinMax2D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(point: Point3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Point3D given in parameter point.

    Args:
        point: Point3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(line: Line3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Line3D given in parameter line.

    Args:
        line: Line3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR)
    """
@typing.overload
def CalcMinMax(polyline: Polyline3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Polyline3D given in parameter polyline.

    Args:
        polyline: Polyline3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYLINE)
    """
@typing.overload
def CalcMinMax(pointCloud: object) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the PointCloud3D given in parameter point cloud.

    Args:
        pointCloud: PointCloud3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYLINE)
    """
@typing.overload
def CalcMinMax(polygon: Polygon3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Polygon3D given in parameter polygon.

    Args:
        polygon: Polygon3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYGON)
    """
@typing.overload
def CalcMinMax(arc: Arc3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Arc3D given in parameter arc.

    Args:
        arc: Arc3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYGON)
    """
@typing.overload
def CalcMinMax(polyhedron: Polyhedron3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Polyhedron3D given in parameter polyhedron.

    Args:
        polyhedron: Polyhedron3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYGON)
    """
@typing.overload
def CalcMinMax(cuboid: Cuboid3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Cuboid3D given in parameter cuboid.

    Args:
        cuboid: Cuboid3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_CUBOID)
    """
@typing.overload
def CalcMinMax(cylinder: Cylinder3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Cylinder3D given in parameter cylinder.

    Args:
        cylinder: Cylinder3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_CYLINDER)
    """
@typing.overload
def CalcMinMax(cone: Cone3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Cone3D given in parameter cylinder.

    Args:
        cone: Cone3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_CONE)
    """
@typing.overload
def CalcMinMax(ellipsoid: Ellipsoid3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the Ellipsoid3D given in parameter ellpsoid.

    Args:
        ellipsoid: Ellipsoid3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_ELLIPSOID)
    """
@typing.overload
def CalcMinMax(area: PolygonalArea3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the PolygonalArea3D given in parameter area.

    Args:
        area: PolygonalArea3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYHEDRON)
    """
@typing.overload
def CalcMinMax(solid: ExtrudedAreaSolid3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the ExtrudedAreaSolid3D given in parameter solid.

    Args:
        solid: ExtrudedAreaSolid3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYHEDRON)
    """
@typing.overload
def CalcMinMax(solid: ClippedSweptSolid3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume by the ClippedSweptSolid3D given in parameter solid.

    Args:
        solid: ClippedSweptSolid3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_POLYHEDRON)
    """
@typing.overload
def CalcMinMax(geo: Path3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D-Min- and Max Point of an element.

    Calculates the MinMax3D volume for the Path3D element.

    Args:
        geo: Path3D to be calculated

    Returns:
        tuple(MinMax3D,
              NO_ERR, INVALID_SURFACE)
    """
@typing.overload
def CalcMinMax(geo: BRep3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate 3D minmax of the B-rep body

    Args:
        geo: BRep3D geometry

    Returns:
        tuple(calculated MinMax3D,
              result code)
    """
def CalcMinMax(self):
    """ Overloaded function. See individual overloads.
    """
def CalcProjectedMinMax(geo: BRep3D, matrix: Matrix3D) -> tuple[MinMax3D, eServiceResult]:
    """Calculate minmax of brep in given projection

    Args:
        geo:    BRep3D to calculate minmax for
        matrix: projection minmax

    Returns:
        tuple(minmax 3D,
              NO_ERR if successful)
    """
def CalcSurface(elem: BRep3D) -> tuple:
    """Calculate surface of BRep3D

    Args:
        elem: input BRep3D

    Returns:
         error code,
        result surface
    """
def CalcVolume(elem: BRep3D) -> tuple:
    """Calculate volume of BRep3D

    Args:
        elem: input BRep3D

    Returns:
         error code,
        result volume
    """
def CalculateNormal(brep: BRep3D, inputPnt: Point3D) -> Vector3D:
    """Calculate normal vector of BRep at point

    Args:
        brep:     BRep
        inputPnt: input point

    Returns:
        normal vector
    """
def CalculateSplineLengthToPoint(spline: Spline2D, splinePointIndex: int) -> float:
    """Calculate spline length from spline start to defined spline point.

    This function returns correct result even if the various points of the spline

    have the same coordinates ( PointLocal(.....) function fails in that case ).

    Args:
        spline:           2D Spline
        splinePointIndex: Spline point index

    Returns:
            Length if everything is OK. -1.0 in case of error.
    """
def Clipping(el1: Line2D, el2: MinMax2D) -> eBoolOpResult:
    """test 2D line and minmax box for clipping

    Args:
        el1: 2D line
        el2: 2D minmax

    Returns:
        eInside (line inside the box), eOutside (line outside the box), eClip
    """
@typing.overload
def Colliding(polygon1: Polygon2D, polygon2: Polygon2D) -> bool:
    """Test for collision between 2 geometry objects

    Args:
        polygon1: the first polygon
        polygon2: the second polygon

    Returns:
        true when colliding, otherwise false.
    """
@typing.overload
def Colliding(polygon: Polygon2D, line: Line2D) -> bool:
    """Test for collision between 2 geometry objects

    Args:
        polygon: polygon
        line:    line

    Returns:
        true when colliding, otherwise false.
    """
@typing.overload
def Colliding(minMax: MinMax2D, polygon: Polygon2D) -> bool:
    """Test for collision between 2 geometry objects

    Args:
        minMax:  MinMax
        polygon: polygon

    Returns:
        true when colliding, otherwise false.
    """
@typing.overload
def Colliding(brep1: BRep3D, brep2: BRep3D) -> bool:
    """Test for collision between 2 breps (touch is not collision)

    Args:
        brep1: 1-st brep element
        brep2: 2-nd brep element

    Returns:
        true when colliding, otherwise false.
    """
def Colliding(self):
    """ Overloaded function. See individual overloads.
    """
def Convert3DRotation(axis: Axis3D, angle: Angle) -> tuple:
    """Convert a 3D Rotation to series of 2D operations: scale, rotation, scale, rotation.

    Args:
        axis:  3D axis
        angle: Angle of 3D rotation

    Returns:
        The first scale in X axis,
        The first scale in Y axis,
        The angle of the first 2D rotation,
        The second scale in X axis (scale in Y axis is 1.0),
        The angle of the second 2D rotation
    """
@typing.overload
def ConvertTo2D(line3D: Line3D) -> tuple[bool, Line2D]:
    """Converts Line3D to Line2D

    Args:
        line3D: Line3D to convert

    Returns:
        tuple(line2D is valid: true/false,
              Converted Line3D)
    """
@typing.overload
def ConvertTo2D(polyline3D: Polyline3D) -> tuple[bool, Polyline2D]:
    """Converts Polyline3D to Polyline2D

    Args:
        polyline3D: Polyline3D to convert

    Returns:
        tuple(polyline2D is valid: true/false,
              Converted Polyline3D)
    """
@typing.overload
def ConvertTo2D(axis3D: Axis3D) -> tuple[bool, Axis2D]:
    """Converts Axis3D to Axis2D

    Args:
        axis3D: Axis3D to convert

    Returns:
        tuple(axis2D is valid: true/false,
              Converted Axis3D)
    """
@typing.overload
def ConvertTo2D(point3D: Point3D) -> tuple[bool, Point2D]:
    """Converts Point3D to Point2D

    Args:
        point3D: Point3D to convert

    Returns:
        tuple(point3D is valid: true/false,
              Converted Point3D)
    """
@typing.overload
def ConvertTo2D(polygon3D: Polygon3D) -> tuple[bool, Polygon2D]:
    """Converts Polygon3D to Polygon2D

    Args:
        polygon3D: Polygon3D to convert

    Returns:
        tuple(polygon3D is valid: true/false,
              Converted Polygon3D)
    """
@typing.overload
def ConvertTo2D(arc3D: Arc3D) -> tuple[bool, Arc2D]:
    """Converts Arc3D to Arc2D

    function converts successfully only 3D circle
    and 3D ellipse which are parallel to standard plane

    Args:
        arc3D: Arc3D to convert

    Returns:
        tuple(Arc3D is valid: true/false,
              Converted Arc3D)
    """
@typing.overload
def ConvertTo2D(spline3D: Spline3D) -> tuple[bool, Spline2D]:
    """Converts Spline3D to Spline2D

    function converts successfully only 3D spline which is parallel to standard plane

    Args:
        spline3D: Spline3D to convert

    Returns:
        tuple(Spline3D is valid: true/false,
              Converted Spline3D)
    """
@typing.overload
def ConvertTo2D(bspline3D: BSpline3D) -> tuple[bool, BSpline2D]:
    """Converts BSpline3D to BSpline2D

    function converts successfully only 3D bspline which is parallel to standard plane

    Args:
        bspline3D: BSpline3D to convert

    Returns:
        tuple(BSpline3D is valid: true/false,
              Converted BSpline3D)
    """
@typing.overload
def ConvertTo2D(points3D: Point3DList) -> tuple[bool, list[Point2D]]:
    """Converts vector of Point3D to vector of Point2D

    Args:
        points3D: points to convert

    Returns:
        tuple(if success true,
              Vector of converted points)
    """
@typing.overload
def ConvertTo2D(path3D: Path3D) -> tuple[bool, Path2D]:
    """Converts Path3D to Path2D

    Args:
        path3D: source path 2D

    Returns:
        tuple(if success true,
              resulting path 3D)
    """
@typing.overload
def ConvertTo2D(geo_object: object) -> object:
    """Converts geometry to 2D geometry

    Currently works on Line3D, Polyline3D, Axis3D, Arc3D, Point3D and Polygon3D.
    2D geometries are cloned without modification.

    Args:
        geo_object: geometry to convert

    Returns:
        nullptr if conversion is not possible, otherwise converted geometry
    """
def ConvertTo2D(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def ConvertTo3D(line2D: Line2D, zPlane: float = 0) -> tuple[bool, Line3D]:
    """Converts Line2D to Line3D

    Args:
        line2D: Line2D to convert
        zPlane: Z value

    Returns:
        tuple(line3D is valid: true/false,
              Converted Line3D)
    """
@typing.overload
def ConvertTo3D(polyline2D: Polyline2D, zPlane: float = 0) -> tuple[bool, Polyline3D]:
    """Converts Polyline2D to Polyline3D

    Args:
        polyline2D: Polyline2D to convert
        zPlane:     Z value

    Returns:
        tuple(polyline3D is valid: true/false,
              Converted Polyline2D)
    """
@typing.overload
def ConvertTo3D(axis2D: Axis2D, zPlane: float = 0) -> tuple[bool, Axis3D]:
    """Converts Axis2D to Axis3D

    Args:
        axis2D: Axis2D to convert
        zPlane: Z value

    Returns:
        tuple(axis3D is valid: true/false,
              Converted Axis3D)
    """
@typing.overload
def ConvertTo3D(spline2D: Spline2D, zPlane: float = 0) -> tuple[bool, Spline3D]:
    """Create an elevated 3D spline from a 2D spline

    Args:
        spline2D: Spline to convert
        zPlane:   Z plane for the spline

    Returns:
        tuple(spline3D is valid: true/false,
              Converted spline3D)
    """
@typing.overload
def ConvertTo3D(arc2D: Arc2D, zPlane: float = 0) -> tuple[bool, Arc3D]:
    """Converts Arc2D to Arc3D

    Args:
        arc2D:  Arc2D to convert
        zPlane: Z value

    Returns:
        tuple(arc3D is valid: true/false,
              Converted Arc2D)
    """
@typing.overload
def ConvertTo3D(bspline2D: BSpline2D, zPlane: float = 0) -> tuple[bool, BSpline3D]:
    """Create an elevated 3D bspline from a 2D bspline

    Args:
        bspline2D: BSpline2D to convert
        zPlane:    Z plane for the spline

    Returns:
        tuple(BSpline3D is valid: true/false,
              Converted BSpline3D)
    """
@typing.overload
def ConvertTo3D(path2D: Path2D, zPlane: float = 0) -> tuple[bool, Path3D]:
    """Convert Path2D to Path3D

    Args:
        path2D: Path2D to convert
        zPlane: Z plane for the curve

    Returns:
        tuple(bool (true = success),
              converted Path3D)
    """
@typing.overload
def ConvertTo3D(points2D: Point2DList, zPlane: float = 0) -> tuple[bool, list[Point3D]]:
    """Convert vector of 2D points to a vector of 3D points

    Args:
        points2D: vector of 2D points
        zPlane:   Z coordinate to be set by conversion

    Returns:
        tuple(true if success,
              vector of converted 3D points)
    """
@typing.overload
def ConvertTo3D(polygon: Polygon2D, zPlane: float = 0) -> tuple[bool, Polygon3D]:
    """Convert 2D polygon to a 3D polygon

    Args:
        polygon: 2D polygon
        zPlane:  Z coordinate to be set by conversion

    Returns:
        tuple(true if success,
              3D polygon)
    """
@typing.overload
def ConvertTo3D(clothoid2D: Clothoid2D, zPlane: float = 0) -> tuple[bool, BSpline3D]:
    """Convert 2D clothoid to a 3D bspline

    Args:
        clothoid2D: 2D clothoid
        zPlane:     Z coordinate to be set by conversion

    Returns:
        tuple(true if success,
              3D bspline)
    """
def ConvertTo3D(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def ConvertToBSpline2D(arc3D: Arc3D) -> tuple[bool, BSpline2D]:
    """Converts Arc3D to BSpline2D

    Args:
        arc3D: Arc3D to convert

    Returns:
        tuple(bspline2D is valid: true/false,
              Converted BSpline2D)
    """
@typing.overload
def ConvertToBSpline2D(spline3D: Spline3D) -> tuple[bool, BSpline2D]:
    """Converts Spline3D to BSpline2D

    Args:
        spline3D: Spline3D to convert

    Returns:
        tuple(bspline2D is valid: true/false,
              Converted BSpline2D)
    """
def ConvertToBSpline2D(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CreateBRep3D(polyhedron: Polyhedron3D) -> tuple:
    """Create BRep3D by converting a polyhedron

    Args:
        polyhedron: polyhedron to convert

    Returns:
         error code,
        BRep3D to create
    """
@typing.overload
def CreateBRep3D(brep: BRep3D, faceindex: int) -> tuple:
    """Create brep from brep face

    Args:
        brep:      brep to copy face from
        faceindex: face index

    Returns:
         error code,
        result brep
    """
def CreateBRep3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreateFrustumOfPyramid(length: float, width: float, height: float, offset: float, bottomPlane: Plane3D) -> tuple:
    """) -> tuple :
    Create a frustum of pyramid

    Args:
        length:      Length of the bottom
        width:       Width of the bottom
        height:      Height of the bottom
        offset:      Offset of the top
        bottomPlane: Bottom plane

    Returns:
        Error code
        Polyhedron
    """
def CreateLoftedBRep3D(outerProfiles: Curve3DList, innerProfiles: Curve3DList, closecaps: bool, createprofileedges: bool, linear: bool,
                       periodic: bool) -> tuple:
    """Create BRep3D by means of lofting through a set of profiles (incl. hole)

    Args:
        outerProfiles:      outer profiles to loft
        innerProfiles:      inner profiles to loft (represents hole in outer profile)
        closecaps:          close brep if possible (all profiles are closed)
        createprofileedges: create profile edges and more surfaces or just create one surface
        linear:             linear or cubic interpolation
        periodic:           if the start profile is also to be the end profile

    Returns:
        tuple(error code,
              result BRep3D)
    """
def CreatePatchBRep3D(curves: list) -> tuple[eCreatePatchResult, BRep3DList]:
    """Create breps as patch from given closed 3D-curves

    Args:
        curves: list of 3D-curves

    Returns:
        tuple(Result of patch creation,
              created BReps)
    """
@typing.overload
def CreatePlanarBRep3D(icurve: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D) -> tuple:
    """Create brep as planar surface

    Args:
        icurve: - border of planar surface ( must be closed )

    Returns:
        tuple(error code,
              - resulting BRep3D ( one planar face ))
    """
@typing.overload
def CreatePlanarBRep3D(profiles: Curve3DList) -> tuple:
    """Create brep as planar surface

    Args:
        profiles: border of planar surface ( must be closed )

    Returns:
        tuple(error code,
              resulting BRep3D ( one planar face ))
    """
def CreatePlanarBRep3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreatePlanarSurface(geometries: list) -> tuple[ePlanarSurfaceError, BRep3DList]:
    """create planar brep

    Args:
        geometries: input geometries pointers

    Returns:
        tuple(surface error code,
              planar surfaces)
    """
@typing.overload
def CreatePolygon3D(polyhedron: Polyhedron3D, faceIndex: int) -> tuple:
    """Creates a Polygon3D element from a Polyhedron face

    Args:
        polyhedron: Polyhedron to get face from
        faceIndex:  Index of the face in polyhedron

    Returns:
         eOK if successful, else eError,
         Created polygon
    """
@typing.overload
def CreatePolygon3D(polygon2D: Polygon2D, plane: Plane3D) -> tuple:
    """Creates a Polygon3D element as a projection of 2D polygon onto given plane

    Args:
        polygon2D: 2D polygon
        plane:     plane to project 2D polygon to

    Returns:
         eOK if successful, else eError,
         Output 3D polygon
    """
@typing.overload
def CreatePolygon3D(polyline: Polyline3D) -> tuple:
    """Creates a Polygon3D from Polyline3D

    Args:
        polyline: 3D polygline

    Returns:
         eOK if successful, else eError,
         Output 3D polygon
    """
def CreatePolygon3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreatePolygon3DFromIndex(arg2: Polygon3D, arg3: int, arg4: int) -> Polygon3D:
    """Create a 3D polygon from a start and end polygon, an index and a division count
    """
@typing.overload
def CreatePolyhedron(polyhedronType: PolyhedronType, verticesCount: int, edgeCount: int, faceCount: int,
                     negativeOrientation: bool) -> tuple:
    """Create and initialize new Polyhedron3D

    Args:
        polyhedronType:      Polyhedron type - edges, faces or volume.
        verticesCount:       Count of expected vertices.
        edgeCount:           Count of expected edges.
        faceCount:           Count of expected faces.
        negativeOrientation: True for negative orientation.

    Returns:
        Error code,
        pointer to 3D Polyhedron which will be created
    """
@typing.overload
def CreatePolyhedron(solid: ClippedSweptSolid3D) -> tuple:
    """Create polyhedron from input parametric solid

    Args:
        solid: clipped swept solid

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(solid: ExtrudedAreaSolid3D) -> tuple:
    """Create polyhedron from input parametric solid

    Args:
        solid: extruded area solid

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(cylinder: Cylinder3D, countOfSegments: int) -> tuple:
    """Create polyhedron from input Cylinder

    Args:
        cylinder:        Cylinder to convert
        countOfSegments: Count of segments

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(igeo: object, options: ApproximationSettings) -> tuple:
    """Create polyhedron from arbitrary solid

    Args:
        geoObject:  Geometry object
        options:    ApproximationSettings structure holding options for approximation

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(brep: BRep3D, options: ApproximationSettings) -> tuple:
    """Create polyhedron as approximation of arbitrary BRep3D

    Args:
        brep:    arbitrary BRep3D
        options: approximation settings

    Returns:
        Error code,
        polyhedron to create
    """
@typing.overload
def CreatePolyhedron(polygon: Polygon3D) -> tuple:
    """Create polyhedron from Polygon3D

    Args:
        polygon: Reference to Polygon3D

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(line: Line3D) -> tuple:
    """Create polyhedron from Line3D

    Args:
        line: Reference to Line3D

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(lines: Line3DList) -> tuple:
    """Create polyhedron from vector of 3D lines

    Args:
        lines: vector of lines

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(polyline: Polyline3D) -> tuple:
    """Create polyhedron from Polyline3D

    Args:
        polyline: Reference to Polyline3D

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(base: Polygon3D, path: Polyline3D) -> tuple:
    """Create translation polyhedron from base polygon and path

    Args:
        base: base polygon
        path: translation path

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(base: Polygon2D, refPoint: Point2D, path: Polyline3D) -> tuple:
    """Create translation polyhedron from base polygon and path

    Args:
        base:     base polygon 2D
        refPoint: reference point used for transformation
        path:     translation path

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
@typing.overload
def CreatePolyhedron(polygon: Polygon2D, bottomPlane: Plane3D, topPlane: Plane3D) -> tuple:
    """Create translation polyhedron from 2D polygon, bottom and top plane

    Args:
        polygon:     polygon 2D
        bottomPlane: the bottom plane
        topPlane:    the top plane

    Returns:
        error code,
        Polyhedron which will be created
    """
@typing.overload
def CreatePolyhedron(baseOutline: Polygon2D, leftOffset: float, rightOffset: float, frontOffset: float, backOffset: float,
                     bottomPlane: Plane3D, topPlane: Plane3D) -> tuple:
    """Create conical polyhedron from 2D polygon, given offsets, bottom and top plane

    Args:
        baseOutline: base outline polygon 2D (rectangle of 4 points)
        leftOffset:  offset from base outline on the left side
        rightOffset: offset from base outline on the right side
        frontOffset: offset from base outline on the front side
        backOffset:  offset from base outline on the back side
        bottomPlane: element's bottom plane
        topPlane:    element's top plane

    Returns:
        Error code,
        polyhedron which will be created
    """
@typing.overload
def CreatePolyhedron(startPolygon: Polygon3D, endPolygon: Polygon3D) -> tuple:
    """Create a polyhedron from a 3D start and end polygon

    Args:
        startPolygon: Start polygon
        endPolygon:   End polygon

    Returns:
        Error code
        Polyhedron
    """
def CreatePolyhedron(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def CreatePolyline3D(polyhedron: Polyhedron3D) -> tuple:
    """Creates a Polyline3D element from a Polyhedron

    Args:
        polyhedron: Polyhedron to create line from

    Returns:
         eOK if converted successful, else eError,
        Created Polyline
    """
@typing.overload
def CreatePolyline3D(polyline2D: Polyline2D) -> tuple:
    """Create Polyline3D from Polyline2D

    Args:
        polyline2D: Reference to Polyline2D

    Returns:
         eOK if created successful, else eError,
        Reference to empty Polyline3D
    """
@typing.overload
def CreatePolyline3D(polygon: Polygon3D) -> tuple:
    """Creates a Polyline3D from Polygon3D

    Args:
        polygon: 3D polygon

    Returns:
         eOK if successful, else eError,
        Output 3D polyline
    """
def CreatePolyline3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreatePolyline3DFromIndex(startPol: Polyline3D, endPol: Polyline3D, index: int, count: int) -> Polyline3D:
    """Create a 3D polyline from a start and end polyline, an index and a division count
    Args:
        startPol: Start polyline
        endPol:   End polyline
        index:    Division index
        count:    Division count

    Returns:
         eOK if converted successful, else eError,
        Created Polyline
    """
@typing.overload
def CreateRailSweptBRep3D(profiles: Curve3DList, rails: Curve3DList, closecaps: bool, uniformScaling: bool,
                          railrotation: bool) -> tuple:
    """Create BRep3D by rail sweeping of profiles. Rails must start/ends on profiles start/end points

    Args:
        profiles:       profiles to sweep
        rails:          rails to control sweeping
        closecaps:      if true, create closed solid if possible, if false just surface(s) will be created
        uniformScaling: use uniform scaling for profiles along the rails
        railrotation:   use rotation the shape to maintain a constant angle with the rail

    Returns:
        tuple(error code,
              result BRep3D (1 swept face))
    """
@typing.overload
def CreateRailSweptBRep3D(profiles: Curve3DList, rails: Curve3DList,
                          path: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D, closecaps: bool, uniformScaling: bool, railrotation: bool, proportionalVertexMatch: bool) -> tuple:
    """Create BRep3D by rail sweeping of profiles. Rails must start/ends on profiles start/end points

    Args:
        profiles:                profiles to sweep
        rails:                   rails to control sweeping
        path:                    user defined path
        closecaps:               if true, create closed solid if possible, if false just surface(s) will be created
        uniformScaling:          use uniform scaling for profiles along the rails
        railrotation:            use rotation the shape to maintain a constant angle with the rail
        proportionalVertexMatch: Flag whether to use proportional vertex matching

    Returns:
        tuple(error code,
              result BRep3D (1 swept face),
              path for body creation)
    """
def CreateRailSweptBRep3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreateRevolvedBRep3D(profiles: Curve3DList, axis: Axis3D, rotationAngle: Angle, closecaps: bool, numprofiles: int) -> tuple:
    """Create brep as revolved body.

    Args:
        profiles:      list of profile curves
        axis:          axis of rotation
        rotationAngle: angle of rotation
        closecaps:     if true, create closed solid if possible, if false just surface(s) will be created
        numprofiles:   number of control profiles created along the created surfaces (division of surface parameter)

    Returns:
        tuple(error code,
              created brep)
    """
@typing.overload
def CreateSweptBRep3D(profile: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D,
                      path: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D, railrotation: bool, rotAxis: (Vector3D | None) = None) -> tuple:
    """Create BRep3D by means of a profile extrusion along a path

    Args:
        profile:      profile to extrude, if closed solid will be created, otherwise a surface only
        path:         path to extrude along
        railrotation: if true, rotate profile along the path
        rotAxis:      if set, profile will be rotated along this axis along the path

    Returns:
        tuple(error code,
              result BRep3D)
    """
@typing.overload
def CreateSweptBRep3D(profiles: Curve3DList, path: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D,
                      closecaps: bool, railrotation: SweepRotationType, rotAxis: (Vector3D | None) = None, numprofiles: int = 0) -> tuple:
    """Create BRep3D by means of a vector of profiles extrusion along a path

    Args:
        profiles:     profiles to extrude, if closed solid will be created, otherwise a surface only
        path:         path to extrude along
        closecaps:    if true, create closed solid if possible, if false just surface(s) will be created
        railrotation: if true, rotate profile along the path
        rotAxis:      if set, profile will be rotated along this axis along the path
        numprofiles:  number of control profiles created along the created surfaces (divisionn of surface parameter)

    Returns:
        tuple(error code,
              result BRep3D)
    """
@PythonPartPylintDecorator.deprecated(replace = " use CreateSweptBRep3D(...) with enum for railrotation")
@typing.overload
def CreateSweptBRep3D(profiles: list, path_object: object, closecaps: bool, railrotation: bool, rotAxis: (Vector3D | None) = None,
                      numprofiles: int = 0) -> tuple[eGeometryErrorCode, BRep3D]:
    """Create BRep3D by means of a vector of profiles extrusion along a path

    Args:
        profiles:        profiles to extrude, if closed solid will be created, otherwise a surface only
        path_object:     path to extrude along
        closecaps:       if true, create closed solid if possible, if false just surface(s) will be created
        railrotation:    if true, rotate profile along the path
        rotAxis:         if set, profile will be rotated along this axis along the path
        numprofiles:     number of control profiles created along the created surfaces (divisionn of surface parameter)

    Returns:
        tuple(error code,
              result BRep3D)
    """
def CreateSweptBRep3D(self):
    """ Overloaded function. See individual overloads.
    """
def CreateSweptPolyhedron3D(profiles: Polyline3DList, path: Polyline3D, closecaps: bool, railrotation: bool,
                            rotAxis: Vector3D) -> tuple:
    """Create translation polyhedron from base polygon and path

    Args:
        profiles:     profiles to sweep
        path:         translation path
        closecaps:    create closed volume (in case of closed profiles) or open shell only
        railrotation: rotate profiles along path - standard rotation = true (keep angle between profile and a path), rotation along z-axis vector = false
        rotAxis:      if set, profile will be rotated along this axis along the path

    Returns:
        Error code,
        Polyhedron3D which will be created
    """
def CutBrepWithPlane(original: BRep3D, plane: Plane3D) -> tuple[bool, BRep3D, BRep3D]:
    """Cut Brep with plane - create two independent BReps

    Args:
        original: original brep
        plane:    cutting plane

    Returns:
        tuple(true if plane cuts the brep. If the plane is above or below brep, it returns false, but one of the result brep is filled with original according to plane position - use brep.IsValid() to check.,
              result brep above the plane,
              result brep below the plane)
    """
def CutPolyhedronWithPlane(original: Polyhedron3D, plane: Plane3D) -> tuple[bool, Polyhedron3D, Polyhedron3D]:
    """Cut polyhedron with plane - create two independent polyhedra

    Args:
        original: original polyhedron
        plane:    cutting plane

    Returns:
        tuple(true if there is a cut, otherwise false, one of polyhedron above/below is filled when whole body is above/below the plane,
              result polyhedron above the plane,
              result polyhedron below the plane)
    """
def DeletePolyhedronLastFace(polyhedron: Polyhedron3D) -> eGeometryErrorCode:
    """Delete the last face of given polyhedron

    Args:
        polyhedron: Polyhedron3D

    Returns:
        Error code
    """
def FaceShell(inputBrep: BRep3D, distance: float, direction: int, faceIndices: NemAll_Python_Utility.VecSizeTList,
              useOffsetStepPierce: bool, useOrthoVXSplit: bool, punchDirection: Vector3D) -> tuple[eGeometryErrorCode, BRep3D]:
    """Execute face shell

    Args:
        inputBrep:           inputBrep
        distance:            distance for offset
        direction:           offset direction 0 - in face normal direction, 1 - in both directions, 2 - opposite to face normal
        faceIndices:         face indexes
        useOffsetStepPierce: if to use offset step pierce
        useOrthoVXSplit:     if to use OrthoVXSplit option
        punchDirection:      defined direction for shell (optional)

    Returns:
        tuple(eOK if success,
              resulting shell BRep)
    """
@typing.overload
def FindMinDistancePoint(point: Point3D, bspline: BSpline3D) -> tuple:
    """Find minimal distance point between Point3D and BSpline3D

    Args:
        point:   Point3D
        bspline: BSpline3D

    Returns:
         error code,
        point on bspline with minimal distance
    """
@typing.overload
def FindMinDistancePoint(point: Point3D, brep: BRep3D) -> tuple:
    """Find minimal distance point between Point3D and BSpline3D

    Args:
        point:   Point3D
        brep:    BRep3D

    Returns:
         error code,
         point on brep with minimal distance
    """
def FindMinDistancePoint(self):
    """ Overloaded function. See individual overloads.
    """
def GetAbsoluteTolerance() -> float:
    """get absolute tolerance

    Returns:
        absolute tolerance
    """
def GetAllIntersections(geoObject1: object, geoObject2: object, eps: float, maxSolutions: int) -> tuple:
    """Calculate all intersections of two geometry objects
    Intersection point must not be located on the elements, it can be outside

    Args:
        geoObject1:   First object
        geoObject2:   Second object
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
def GetAngleTolerance() -> Angle:
    """Get angle tolerance

    This tolerance is using for angle comparison.
    Use it with Comparison::Equal(value, value, GetAngleTolerance())

    Returns:
        Tolerance using for angle comparison [rad]
    """
def GetClosestIntersection(geometrie1: object, geometrie2: object, inputPoint: Point3D, eps: float, bOnlyInsidePoints: bool) -> tuple:
    """Function to calculate the nearest intersection between two geometries to a reference point
    Intersection point must not be located on the elements, it can be outside

    Args:
        geometrie1:        First object
        geometrie2:        Second object
        inputPoint:        Reference Point / Cursor point
        eps:               Tolerance
        bOnlyInsidePoints: Return point must be on both objects

    Returns:
        true, if an intersection was found, otherwise false,
        intersection point
    """
def GetCurvatureTolerance() -> float:
    """Get curvature tolerance

    This tolerance is using for curvature comparison.
    Use it with Comparison::Equal(value, value, GetCurvatureTolerance())

    Returns:
        Tolerance using for curvature comparison
    """
def GetCurveLengthTolerance() -> float:
    """Get tolerance for curve length comparison

    This tolerance is using for length of curve comparison.
    Use it with Comparison::Equal(value, value, GetCurveLengthTolerance())

    Returns:
        Tolerance using for length of curve comparison [mm]
    """
def GetIntersectionPoints(geoObject1: object, geoObject2: object, eps: float) -> tuple:
    """Function to calculate the nearest intersection between two geometries to a reference point
    Intersection point must not be located on the elements, it can be outside

    Args:
        geoObject1: First object
        geoObject2: Second object
        eps:        Tolerance (optional)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector of intersection points and additional information
    """
def GetRelativeTolerance() -> float:
    """get relative tolerance

    Returns:
        relative tolerance
    """
@typing.overload
def GetRotationMatrix(zeroPoint: Point2D, angle: Angle) -> Matrix2D:
    """Creates 2D rotation matrix

    Args:
        zeroPoint: Rotation point
        angle:     Rotation angle

    Returns:
         2D rotation matrix
    """
@typing.overload
def GetRotationMatrix(axis: Axis3D, angle: Angle) -> Matrix3D:
    """Creates 3D rotation matrix

    Args:
        axis:  Rotation axis
        angle: Rotation angle

    Returns:
         3D rotation Matrix
    """
@typing.overload
def GetRotationMatrix(line: Line3D, angle: Angle) -> Matrix3D:
    """Creates 3D rotation matrix

    Args:
        line:  Rotation line, extended to axis
        angle: Rotation angle

    Returns:
         3D rotation Matrix
    """
def GetRotationMatrix(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def GroundViewHiddenCalculation(brep: BRep3D) -> tuple[eGeometryErrorCode, list[typingAny], list[typingAny]]:
    """Hidden calculation with ground view of BRep

    Args:
        brep: BRep

    Returns:
        tuple(Error code,
              Vector of visible edges,
              Vector of hidden edges)
    """
@typing.overload
def GroundViewHiddenCalculation(poly: Polyhedron3D) -> tuple[eGeometryErrorCode, list[Line3D], list[Line3D]]:
    """Hidden calculation with ground view of polyhedron.

    Args:
        poly: polyhedron

    Returns:
        tuple(Error code,
              Vector of visible edges,
              Vector of hidden edges)
    """
def GroundViewHiddenCalculation(self):
    """ Overloaded function. See individual overloads.
    """
def ImprintProfileOnFaces(brep: BRep3D, targetFaces: (list[int] | NemAll_Python_Utility.VecUIntList),
                          profile: Arc3D | BSpline3D | Line3D | Path3D | Polyline3D | Polygon3D | Spline3D) -> tuple:
    """Imprint edges on brep

    Args:
        brep:        Brep
        targetFaces: faces where to imprint edges
        profile:     imprinted profile

    Returns:
        tuple(eOK if successful otherwise eError,
              Brep,
              new faces after imprint)
    """
@typing.overload
def Intersect(bodies1: PolyhedronTypesList, bodies2: PolyhedronTypesList) -> tuple:
    """compute intersection of set of bodies

    Args:
        bodies1: list of bodies
        bodies2: list of bodies

    Returns:
        tuple(true when intersecting, otherwise false.,
              resulted polyhedron)
    """
@typing.overload
def Intersect(el1: Plane3D, el2: Plane3D) -> tuple[bool, Axis3D]:
    """calculate intersection between 2 3D planes

    Args:
        el1: the first plane
        el2: the second plane

    Returns:
        tuple(true when intersecting, otherwise false.,
              common axis of planes)
    """
@typing.overload
def Intersect(el1: Polyhedron3D, el2: Polyhedron3D) -> tuple[bool, Polyhedron3D]:
    """compute intersection of 2 3D polyhedron

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        tuple(true when intersecting, otherwise false.,
              resulted polyhedron)
    """
@typing.overload
def Intersect(brep1: BRep3D, brep2: BRep3D) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute intersection of 2 breps

    Args:
        brep1: first brep
        brep2: second brep

    Returns:
        tuple(true when intersecting, otherwise false.,
              result brep of intersection)
    """
@typing.overload
def Intersect(brep: BRep3D, polyhedron: Polyhedron3D) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute intersection of 2 bodies

    Args:
        brep:       first element - BRep3D
        polyhedron: second element - Polyhedron3D

    Returns:
        tuple(error code,
              result BRep3D)
    """
def Intersect(self):
    """ Overloaded function. See individual overloads.
    """
def IntersectRayBRep(rayPoint: Point3D, rayVector: Vector3D, brep: BRep3D, bNegativPrefered: bool) -> tuple[int, IntersectionRayBRep]:
    """Intersection of Ray and BRep

    Args:
        rayPoint:         ray Point
        rayVector:        direction vector of ray
        brep:             BRep
        bNegativPrefered: if true -> return first solution when ray point is out of object

    Returns:
        tuple(0 if no error occurs,
              structure with result of intersection)
    """
def IntersectRayPolyhedron(rayPoint: Point3D, rayVector: Vector3D, polyhedron: Polyhedron3D, flag: IntersectRayPolyhedronFlag,
                           selFaces: ((list[int] | NemAll_Python_Utility.VecIntList) | None) = None, searchDistance: float = 0.0, pixelSize: float = 0) -> tuple[int, IntersectionRayPolyhedron]:
    """Intersection of Ray and Polyhedron

    Args:
        rayPoint:       ray Point
        rayVector:      direction vector of ray
        polyhedron:     polyhedron
        flag:           flag for determining the "best" intersection
        selFaces:       optional list of faces used for intersection, if default value is used, all faces are checked
        searchDistance: used for eNegativeVerticalPreferred to find vertical faces near point found on not-vertical face
        pixelSize:      in mm used for eNegativeVerticalPreferred to find vertical faces

    Returns:
        tuple(0 if no error occurred,
              structure with result of intersection)
    """
@typing.overload
def Intersecting(el1: MinMax2D, el2: MinMax2D) -> bool:
    """test 2 2D minmaxes for intersection

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        true when intersecting, otherwise false.
    """
@typing.overload
def Intersecting(el1: Line2D, el2: Line2D, tol: float) -> bool:
    """test 2 2D lines for intersection

    Args:
        el1: 1. element
        el2: 2. element
        tol: tolerance

    Returns:
        true when intersecting, otherwise false.
    """
@typing.overload
def Intersecting(el1: Polygon2D, el2: Polygon2D, tol: float) -> bool:
    """test 2 2D polygons for intersection
       throw Exception in case of internal error.

    Args:
        el1: 1. element
        el2: 2. element
        tol: tolerance

    Returns:
        true when intersecting, otherwise false.
    """
@typing.overload
def Intersecting(el1: BRep3D, el2: BRep3D) -> bool:
    """test 2 breps for intersection

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: BRep3D, el2: Polyhedron3D) -> bool:
    """test brep and polyhedron for intersection

    Args:
        el1: brep to check
        el2: polyhedron to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: Arc3D, el2: Polyhedron3D) -> bool:
    """test 3D arc and polyhedron for intersection

    Args:
        el1: arc to check
        el2: polyhedron to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: Arc3D, el2: BRep3D) -> bool:
    """test 3D arc and brep for intersection

    Args:
        el1: arc to check
        el2: brep to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: Spline3D, el2: Polyhedron3D) -> bool:
    """test 3D spline and polyhedron for intersection

    Args:
        el1: spline to check
        el2: polyhedron to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: Spline3D, el2: BRep3D) -> bool:
    """test 3D spline and brep for intersection

    Args:
        el1: spline to check
        el2: brep to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: BSpline3D, el2: Polyhedron3D) -> bool:
    """test 3D bspline and polyhedron for intersection

    Args:
        el1: bspline to check
        el2: polyhedron to check

    Returns:
        bool true when intersecting
    """
@typing.overload
def Intersecting(el1: BSpline3D, el2: BRep3D) -> bool:
    """test 3D bspline and brep for intersection

    Args:
        el1: bspline to check
        el2: brep to check

    Returns:
        bool true when intersecting
    """
def Intersecting(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def IntersectingRel(el1: MinMax2D, el2: MinMax2D) -> bool:
    """test 2 geo 2D minmaxes for intersection using built-in relative tolerance

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        true when intersecting, otherwise false.
    """
@typing.overload
def IntersectingRel(el1: Line2D, el2: Line2D) -> bool:
    """test 2 2D lines for intersection

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        true when intersecting, otherwise false.
    """
def IntersectingRel(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def IntersectionCalculus(el1: Axis2D, el2: Axis2D) -> tuple:
    """compute intersection of 2 2D axis

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        true when intersecting, otherwise false.,
        result intersection point if possible
    """
@typing.overload
def IntersectionCalculus(axis: Axis2D, line: Line2D) -> tuple:
    """compute intersection between 2D axis and 2D line

    Args:
        axis: 2D Axis
        line: 2D line

    Returns:
        true when intersecting, otherwise false.,
        result intersection point if possible
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, axis3D: Axis3D) -> tuple:
    """Calculate the intersection between a 2D and a 3D axis

    Args:
        axis2D: 2D Axis
        axis3D: 3D Axis

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, arc2D: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D arc

    emarks There are known precision issues with the background function lksplk

    Args:
        axis2D: 2D Axis
        arc2D:  2D Arc
        eps:    precision

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D polyline

    Args:
        axis2D:   2D Axis
        polyline: 2D Polyline

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D polygon

    Args:
        axis2D:  2D Axis
        polygon: 2D Polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D spline

    Args:
        axis2D:       2D Axis
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis2D: Axis2D, bspline: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D bspline

    Args:
        axis2D:       2D Axis
        bspline:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis1: Axis3D, axis2: Axis3D) -> tuple:
    """Calculate the intersection between two 3D axis

    Args:
        axis1: First 3D Axis
        axis2: Second 3D Axis

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, line: Line2D) -> tuple:
    """Calculate the intersection between 3D axis and 2D line

    Args:
        axis: 3D Axis
        line: 2D line

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, arc: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D arc

    emarks There are known precision issues with the background function lksplk

    Args:
        axis: 3D Axis
        arc:  2D Arc
        eps:  precision

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D polyline

    Args:
        axis:     3D Axis
        polyline: 2D Polyline

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D polygon

    Args:
        axis:    3D Axis
        polygon: 2D Polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D spline

    Args:
        axis:         3D Axis
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D spline

    Args:
        axis:         3D Axis
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, spline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D B-spline

    Args:
        axis:         3D Axis
        spline:       3D B-Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, plane: Plane3D, eps: float) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D plane

    Args:
        axis:  3D Axis
        plane: 3D Plane
        eps:   Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(line: Line3D, plane: Plane3D, eps: float) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D plane

    Args:
        line:  3D Line
        plane: 3D Plane
        eps:   Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(axis: Axis3D, arc: Arc3D, eps: float) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D arc

    Args:
        axis: 3D Axis
        arc:  3D Arc
        eps:  Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, arc: Arc3D, eps: float) -> tuple:
    """Calculate the intersection between a 3D line and a 3D arc

    Args:
        line: 3D Line
        arc:  3D Arc
        eps:  Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection points
    """
@typing.overload
def IntersectionCalculus(el1: Line2D, el2: Line2D) -> tuple:
    """compute intersection of 2 2D line

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        true when intersecting, otherwise false.,
        result intersection point if possible
    """
@typing.overload
def IntersectionCalculus(line2D: Line2D, line3D: Line3D) -> tuple:
    """Calculate the intersection between a 2D and a 3D line

    Args:
        line2D: 2D Line
        line3D: 3D Line

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(line2D: Line2D, arc2D: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D line and a 2D arc

    emarks There are known precision issues with the background function lksplk

    Args:
        line2D: 2D Line
        arc2D:  2D Arc
        eps:    precision

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line2D: Line2D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 2D line and a 2D polyline

    Args:
        line2D:   2D Line
        polyline: 2D Polyline

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line2D: Line2D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 2D line and a 2D polygon

    Args:
        line2D:  2D Line
        polygon: 2D Polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line2D, bspline: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 2D bspline

    Args:
        line:         2D Line
        bspline:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line2D: Line2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 2D spline

    Args:
        line2D:       2D Line
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line1: Line3D, line2: Line3D) -> tuple:
    """Calculate the intersection between two 3D line

    Args:
        line1: First 3D Line
        line2: Second 3D Line

    Returns:
            true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculus(line: Line3D, arc: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 3D line and a 2D arc

    emarks There are known precision issues with the background function lksplk

    Args:
        line: 3D Line
        arc:  2D Arc
        eps:  precision

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 3D line and a 2D polyline

    Args:
        line:     3D Line
        polyline: 2D Polyline

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 3D line and a 2D polygon

    Args:
        line:    3D Line
        polygon: 2D Polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 2D spline

    Args:
        line:         3D Line
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 3D spline

    Args:
        line:         3D Line
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(line: Line3D, bspline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 3D bspline

    Args:
        line:         3D Line
        bspline:      3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc1: Arc2D, arc2: Arc2D) -> tuple:
    """Calculate the intersection between two arcs

    Args:
        arc1: 2D Arc
        arc2: 2D Arc

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc2D, polyline: Polyline2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D polyline

    emarks There are known precision issues with the background function lksplk

    Args:
        arc:      2D Arc
        polyline: 2D Polyline
        eps:      precision

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc2D, polygon: Polygon2D, intersectionPnts: float) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D polygon

    emarks There are known precision issues with the background function lksplk

    Args:
        arc:              2D Arc
        polygon:          2D Polygon
        intersectionPnts: Vector which includes all resulting intersection points

    Returns:
            true, if an intersection was found, otherwise false,
        precision
    """
@typing.overload
def IntersectionCalculus(arc: Arc2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D spline

    Args:
        arc:          2D Arc
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc2D, bspline: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D spline

    Args:
        arc:          2D Arc
        bspline:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc3D, arc2: Arc3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D arc and a 3D B-spline

    Args:
        arc:          First 3D Arc
        arc2:         Second 3D Arc
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D arc and a 3D spline

    Args:
        arc:          3D Arc
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(arc: Arc3D, bspline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D arc and a 3D B-spline

    Args:
        arc:          3D Arc
        bspline:      3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polyline1: Polyline2D, polyline2: Polyline2D) -> tuple:
    """Calculate the intersection between two polylines

    Args:
        polyline1: 2D polyline
        polyline2: 2D polyline

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polyline: Polyline2D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between polyline and polygon

    Args:
        polyline: 2D polyline
        polygon:  2D polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polygon1: Polygon2D, polygon2: Polygon2D) -> tuple:
    """Calculate the intersection between two polygons

    Args:
        polygon1: 2D polygon
        polygon2: 2D polygon

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polyline: Polyline2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D polyline and a 2D spline

    Args:
        polyline:     First 2D polyline
        spline:       Second 2D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polyline: Polyline2D, spline: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D polyline and a 2D bspline

    Args:
        polyline:     2D Polyline
        spline:       2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polyline: Polyline3D, spline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D polyline and a 3D bspline

    Args:
        polyline:     3D Polyline
        spline:       3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(polygon: Polygon2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D polygon and a 2D spline

    Args:
        polygon:      First 2D polygon
        spline:       Second 2D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(plane: Plane3D, line: Line3D, eps: float) -> tuple:
    """Calculate the intersection between 3D plane and 3D line

    Args:
        plane: 3D plane
        line:  3D line
        eps:   Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(plane: Plane3D, line: Polyline3D, eps: float) -> tuple:
    """Calculate the intersection between 3D plane and 3D polyline

    Args:
        plane: 3D plane
        line:  3D polyline
        eps:   Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(plane: Plane3D, arc: Arc3D, eps: float) -> tuple:
    """Calculate the intersection between 3D plane and 3D arc

    Args:
        plane: 3D plane
        arc:   3D arc
        eps:   Tolerance

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(plane: Plane3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between 3D plane and 3D arc

    Args:
        plane:        3D plane
        spline:       3D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: Spline2D, spline2: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between two 2D splines

    Args:
        spline1:      First 2D spline
        spline2:      Second 2D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: Spline2D, spline2: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between 2D spline and 3D spline

    ote 2D spline is converted to 3D spline and calculation between 3D splines is called

    Args:
        spline1:      First 2D spline
        spline2:      Second 3D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: Spline3D, spline2: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D Spline and a 3D Spline

    Args:
        spline1:      3D Spline
        spline2:      3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: Spline2D, spline2: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D Spline and a 2D BSpline

    Args:
        spline1:      2D Spline
        spline2:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: Spline3D, spline2: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D BSpline and a 3D Spline

    Args:
        spline1:      3D Spline
        spline2:      3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: BSpline2D, spline2: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D BSpline and a 2D BSpline

    Args:
        spline1:      2D BSpline
        spline2:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(spline1: BSpline3D, spline2: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D BSpline and a 3D BSpline

    Args:
        spline1:      3D BSpline
        spline2:      3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
            true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculus(ele1: object, ele2: object, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D axis and a 3D spline

    Args:
        ele1:         First element
        ele2:         Second element
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
            true, if an intersection was found, otherwise false,
            Vector which includes all resulting intersection points
    """
def IntersectionCalculus(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def IntersectionCalculusEx(axis2D: Axis2D, arc2D: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D arc
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        axis2D: 2D Axis
        arc2D:  2D Arc
        eps:    precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis2D: Axis2D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D polyline
    Intersection point must not be located on the elements, it can be outside

    Args:
        axis2D:   2D Axis
        polyline: 2D Polyline

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis2D: Axis2D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    Args:
        axis2D:  2D Axis
        polygon: 2D Polygon

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis2D: Axis2D, clothoid2D: Clothoid2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D axis and a 2D clothoid
    Intersection point must not be located on the elements, it can be outside

    Args:
        axis2D:       2D axis
        clothoid2D:   2D Clothoid
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis: Axis3D, arc: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D arc
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        axis: 3D Axis
        arc:  2D Arc
        eps:  precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis: Axis3D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D polyline
    Intersection point must not be located on the elements, it can be outside

    Args:
        axis:     3D Axis
        polyline: 2D Polyline

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(axis: Axis3D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 3D axis and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    Args:
        axis:    3D Axis
        polygon: 2D Polygon

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line1: Line2D, line2: Line2D) -> tuple:
    """Calculate the intersection between two 2D lines.
    Intersection point must not be located on the elements, it can be outside

    Args:
        line1: First 2D Line
        line2: Second 2D Line

    Returns:
        true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, line3D: Line3D) -> tuple:
    """Calculate the intersection between a 2D and a 3D line
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D: 2D Line
        line3D: 3D Line

    Returns:
        true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, arc2D: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D line and a 2D arc
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        line2D: 2D Line
        arc2D:  2D Arc
        eps:    precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, clothoid2D: Clothoid2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 2D clothoid
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D:       2D Line
        clothoid2D:   2D Clothoid
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 2D line and a 2D polyline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D:   2D Line
        polyline: 2D Polyline

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 2D line and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D:  2D Line
        polygon: 2D Polygon

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 2D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D:       2D Line
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 3D spline
    Intersection point must not be located on the elements, it can be outside

    ote 2D line is converted to 3D line and calculation between 3D line and 3D spline is called

    Args:
        line2D:       2D Line
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line2D: Line2D, bspline: BSpline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D line and a 2D bspline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line2D:       2D Line
        bspline:      2D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line1: Line3D, line2: Line3D) -> tuple:
    """Calculate the intersection between two 3D line
    Intersection point must not be located on the elements, it can be outside

    Args:
        line1: First 3D Line
        line2: Second 3D Line

    Returns:
        true, if an intersection was found, otherwise false,
        Resulting intersection point
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, arc: Arc2D, eps: float) -> tuple:
    """Calculate the intersection between a 3D line and a 2D arc
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        line: 3D Line
        arc:  2D Arc
        eps:  precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, arc: Arc3D, eps: float) -> tuple:
    """Calculate the intersection between a 3D line and a 3D arc
    Intersection point must not be located on the elements, it can be outside

    Args:
        line: 3D Line
        arc:  3D Arc
        eps:  precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, clothoid: Clothoid2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 2D clothoid
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:         3D Line
        clothoid:     2D Clothoid
        eps:          Tolerance
        maxSolutions: Maximum number of solutions (Defines the maximum size of the solution vector)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, polyline: Polyline2D) -> tuple:
    """Calculate the intersection between a 3D line and a 2D polyline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:     3D Line
        polyline: 2D Polyline

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, polygon: Polygon2D) -> tuple:
    """Calculate the intersection between a 3D line and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:    3D Line
        polygon: 2D Polygon

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 2D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:         3D Line
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 3D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:         3D Line
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(line: Line3D, spline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D line and a 3D bspline
    Intersection point must not be located on the elements, it can be outside

    Args:
        line:         3D Line
        spline:       3D BSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc1: Arc2D, arc2: Arc2D) -> tuple:
    """Calculate the intersection between two arcs
    Intersection point must not be located on the elements, it can be outside

    Args:
        arc1: 2D Arc
        arc2: 2D Arc

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc2D, clothoid: Clothoid2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D clothoid
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function kurve6 which is only
    correct for circles

    Args:
        arc:          2D Arc
        clothoid:     2D Clothoid
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc2D, polyline: Polyline2D, eps: float) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D polyline
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        arc:      2D Arc
        polyline: 2D Polyline
        eps:      precision

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc2D, polygon: Polygon2D, intersectionPnts: float) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    emarks There are known precision issues with the background function lksplk

    Args:
        arc:              2D Arc
        polygon:          2D Polygon
        intersectionPnts: Vector which includes all resulting intersection points

    Returns:
        true, if an intersection was found, otherwise false,
        precision
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D arc and a 2D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        arc:          2D Arc
        spline:       2D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc2D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D arc and a 3D spline
    Intersection point must not be located on the elements, it can be outside

    ote 2D arc is converted to 3D arc and calculation between 3D arc and 3D spline is called

    Args:
        arc:          2D Arc
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc1: Arc3D, arc2: Arc3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between two arcs
    Intersection point must not be located on the elements, it can be outside

    Args:
        arc1:         3D Arc
        arc2:         3D Arc
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc3D, spline: Spline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D arc and a 3D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        arc:          3D Arc
        spline:       3D Spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(arc: Arc3D, spline: BSpline3D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 3D arc and a 3D bspline
    Intersection point must not be located on the elements, it can be outside

    Args:
        arc:          3D Arc
        spline:       3D bSpline
        eps:          Tolerance
        maxSolutions: Maximum number of solution

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(clothoid: Clothoid2D, polyline: Polyline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a clothoid and a polyline
    Intersection point must not be located on the elements, it can be outside

    Args:
        clothoid:     2D clothoid
        polyline:     2D polyline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(clothoid: Clothoid2D, polygon: Polygon2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a clothoid and a 2D polygon
    Intersection point must not be located on the elements, it can be outside

    Args:
        clothoid:     2D clothoid
        polygon:      2D polygon
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(polyline1: Polyline2D, polyline2: Polyline2D) -> tuple:
    """Calculate the intersection between two 2D polylines
    Intersection point must not be located on the elements, it can be outside

    Args:
        polyline1: 2D polyline
        polyline2: 2D polyline

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(polygon1: Polygon2D, polygon2: Polygon2D) -> tuple:
    """Calculate the intersection between two 2D polygons
    Intersection point must not be located on the elements, it can be outside

    Args:
        polygon1: 2D polygon
        polygon2: 2D polygon

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(polyline: Polyline2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D polyline and a 2D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        polyline:     First 2D polyline
        spline:       Second 2D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(polygon: Polygon2D, spline: Spline2D, eps: float, maxSolutions: int) -> tuple:
    """Calculate the intersection between a 2D polygon and a 2D spline
    Intersection point must not be located on the elements, it can be outside

    Args:
        polygon:      First 2D polygon
        spline:       Second 2D spline
        eps:          Tolerance
        maxSolutions: Maximum number of solution (especially for splines and clothoids)

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
@typing.overload
def IntersectionCalculusEx(geoObject1: object, geoObject2: object, eps: float, maxSolutions: int, bOnlyInsidePoints: bool) -> tuple:
    """Calculate intersections between two geometry objects
    Intersection points must not be located on the elements, it can be outside

    Args:
        geoObject1:        First object
        geoObject2:        Second object
        eps:               Tolerance
        maxSolutions:      Maximum number of solution (especially for splines and clothoids)
        bOnlyInsidePoints: Intersection points must be on both objects

    Returns:
        true, if an intersection was found, otherwise false,
        Vector which includes all resulting intersection points
    """
def IntersectionCalculusEx(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def IsCoplanar(geoVector_object: list) -> tuple[bool, Plane3D]:
    """Check if the 3D geometry objects are coplanar and calculate plane

    Args:
        geoVector_object: vector of object geometries

    Returns:
        tuple(True if objects are coplanar, false otherwise.,
              result plane - if collinear plane is not valid)
    """
@typing.overload
def IsCoplanar(igeo1_object: object, igeo2_object: object) -> tuple[bool, Plane3D, bool]:
    """Check if two 3D curved geometry objects are coplanar and calculate plane

    Args:
        igeo1_object: first object geometry
        igeo2_object: second object geometry

    Returns:
        tuple(True if objects are coplanar, false otherwise.,
              result plane,
              flag if lines are parallel)
    """
@typing.overload
def IsCoplanar(plane: Plane3D, geo_object: object) -> bool:
    """Find out if plane and geometry are coplanar

    Args:
        plane:      Plane3D
        geo_object: objects geometry

    Returns:
        True, if geometry is lying in the plane otherwise return false.
    """
@typing.overload
def IsCoplanar(plane: Plane3D, point: Point3D) -> bool:
    """Find out if point lies on plane

    Args:
        plane: Plane3D
        point: Point3D

    Returns:
        True, if point lies on plane otherwise return false.
    """
@typing.overload
def IsCoplanar(plane: Plane3D, line: Line3D) -> bool:
    """Find out if line lies on plane

    Args:
        plane: Plane3D
        line:  Line3D

    Returns:
        True, if line lies on plane otherwise return false.
    """
@typing.overload
def IsCoplanar(plane1: Plane3D, plane2: Plane3D) -> bool:
    """Find out if planes are coplanar

    Args:
        plane1: Plane3D
        plane2: Plane3D

    Returns:
        True, if planes are coplanar otherwise return false.
    """
@typing.overload
def IsCoplanar(point1: Point3D, point2: Point3D, point3: Point3D, point4: Point3D) -> bool:
    """Find out if four points are coplanar

    Args:
        point1: Point3D
        point2: Point3D
        point3: Point3D
        point4: Point3D

    Returns:
        True, if points are coplanar otherwise return false.
    """
@typing.overload
def IsCoplanar(line1: Line3D, line2: Line3D) -> bool:
    """Find out if two lines are coplanar

    Args:
        line1: Line3D
        line2: Line3D

    Returns:
        True, if lines are coplanar otherwise return false.
    """
@typing.overload
def IsCoplanar(line1: Line3D, line2: Line3D) -> tuple[bool, Plane3D]:
    """Check if lines are coplanar and calculate plane

    Args:
        line1: Line3D
        line2: Line3D]

    Returns:
        tuple(True, if lines are coplanar.,
              result plane)
    """
def IsCoplanar(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def MakeBoolean(el1: Line2D, el2: Polygon2D) -> tuple[eGeometryErrorCode, Line2DList, Line2DList]:
    """make boolean operation between line and polygon

    Args:
        el1: Line2D
        el2: Polygon2D

    Returns:
        tuple(GeoErrorCode,
              set of line segments which are inside input polygon, NULL if not desired,
              set of line segments which are outside input polygon, NULL if not desired)
    """
@typing.overload
def MakeBoolean(el1: Polygon2D, el2: Polygon2D) -> tuple[eGeometryErrorCode, Polygon2D, Polygon2D, Polygon2D, Polygon2D]:
    """make boolean operation between two 2D profile elements

    Now it is done for Polygon2D, later with new Profile element.

    Args:
        el1: first element geometry
        el2: second element geometry

    Returns:
        tuple(GeoErrorCode,
              output 2D profile of intersection,
              output 2D profile of union,
              output 2D profile of subtraction element1 minus element2,
              output 2D profile of subtraction element2 minus element1)
    """
@typing.overload
def MakeBoolean(el1: Polyhedron3D, el2: Polyhedron3D) -> tuple[eGeometryErrorCode, Polyhedron3D, Polyhedron3D, Polyhedron3D,
                Polyhedron3D]:
    """make boolean operation between two 3D bodies

    As input arbitrary element which represents 3D is possible.

    Throws exception when element is not suitable for booleans

    Args:
        el1: first element geometry
        el2: second element geometry

    Returns:
        tuple(GeoErrorCode,
              output 3D body of intersection,
              output 3D body of union,
              output 3D body of subtraction element1 minus element2,
              output 3D body of subtraction element2 minus element1)
    """
def MakeBoolean(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def MakeIntersection(brep1: BRep3D, breps: BRep3DList) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute intersection of 2 breps

    Args:
        brep1: first brep
        breps: second brep

    Returns:
        tuple(eOK if intersection was successful,
              result brep of intersection)
    """
@PythonPartPylintDecorator.deprecated(replace = " use Intersect(...)")
@typing.overload
def MakeIntersection(brep1: BRep3D, brep2: BRep3D) -> tuple:
    """Deprecated: use Intersect(...)

    Args:
        brep1: first brep
        brep2: second brep

    Returns:
        error code, eOK if intersection was successful,
        result brep of intersection
    """
@PythonPartPylintDecorator.deprecated(replace = " use Intersect(...)")
@typing.overload
def MakeIntersection(brep: BRep3D, polyhedron: Polyhedron3D) -> tuple:
    """Deprecated: use Intersect(...)

    Args:
        brep:       first element - BRep3D
        polyhedron: second element - Polyhedron3D

    Returns:
         error code,
        result BRep3D
    """
@PythonPartPylintDecorator.deprecated(replace = " use Intersect(...)")
@typing.overload
def MakeIntersection(el1: Polyhedron3D, el2: Polyhedron3D) -> tuple:
    """Deprecated: use Intersect(...)

    Args:
        el1: 1. element
        el2: 2. element

    Returns:
        error code, eOK if intersection was successful,
        resulted polyhedron
    """
def MakeIntersection(self):
    """ Overloaded function. See individual overloads.
    """
def MakeSectionWithSurfaces(brep1: BRep3D, brep2: BRep3D) -> tuple[eGeometryErrorCode, BRep3DList]:
    """Compute section of brep and surface brep

    Args:
        brep1: first brep
        brep2: section brep

    Returns:
        tuple(error code,
              section resulting breps)
    """
@typing.overload
def MakeSubtraction(body: Polyhedron3D | Cylinder3D | ExtrudedAreaSolid3D | Line3D | Polyline3D | Polygon3D | ClippedSweptSolid3D,
                    voidbodies: PolyhedronTypesList) -> tuple:
    """make subtraction of 3D bodies from given body

    Args:
        body:       input body
        voidbodies: list of 3D bodies to subtract

    Returns:
        tuple(GeoErrorCode,
              output 3D body of subtraction)
    """
@typing.overload
def MakeSubtraction(poly1: Polygon2D, poly2: Polygon2D) -> tuple[eGeometryErrorCode, Polygon2D, Polygon2D]:
    """make subtraction of 2D polygons, if wished intersection is computed too.

    Args:
        poly1: first polygon
        poly2: second polygon

    Returns:
        tuple(GeoErrorCode,
              output 2D polygon of subtraction,
              output 2D polygon of intersection)
    """
@typing.overload
def MakeSubtraction(polyhed1: Polyhedron3D, polyhed2: Polyhedron3D) -> tuple[eGeometryErrorCode, Polyhedron3D]:
    """make subtraction of polyhed1 - polyhed2

    Args:
        polyhed1: first polyhedron
        polyhed2: second polyhedron

    Returns:
        tuple(GeoErrorCode,
              result 3D polyhedron of subtraction)
    """
@typing.overload
def MakeSubtraction(brep1: BRep3D, brep2: BRep3D) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute subtraction of 2 breps

    Args:
        brep1: first brep
        brep2: second brep to be subtracted from the first brep

    Returns:
        tuple(error code,
              result brep of subtraction)
    """
@typing.overload
def MakeSubtraction(brep1: BRep3D, breps: BRep3DList) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute subtraction of brep and vector of breps

    Args:
        brep1: first brep
        breps: vector of brep to be subtracted from the first brep

    Returns:
        tuple(error code,
              result brep of subtraction)
    """
@PythonPartPylintDecorator.deprecated(replace = " use MakeSubtraction(const Polygon2D& poly1, const Polygon2D& poly2)")
@typing.overload
def MakeSubtraction(poly1: Polygon2D, poly2: Polygon2D, intersection: Polygon2D) -> tuple:
    """Deprecated: use MakeSubtraction(const Polygon2D& poly1, const Polygon2D& poly2)

    make subtraction of 2D polygons, if wished intersection is computed too.

    Args:
        poly1:        first polygon
        poly2:        second polygon
        intersection: output 2D polygon of intersection, as input NULL if not required

    Returns:
        GeoErrorCode,
        output 2D polygon of subtraction
    """
def MakeSubtraction(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def MakeUnion(bodies: PolyhedronTypesList, voidbodies: PolyhedronTypesList) -> tuple:
    """make union of 3D bodies

    As input arbitrary elements which represents 3D is possible.

    Args:
        bodies:     list of 3D bodies
        voidbodies: list of 3D bodies to subtract

    Returns:
        tuple(GeoErrorCode,
              output 3D body of union)
    """
@typing.overload
def MakeUnion(poly1: Polygon2D, poly2: Polygon2D) -> tuple[eGeometryErrorCode, Polygon2D]:
    """make union of 2D polygons

    Args:
        poly1: first polygon
        poly2: second polygon

    Returns:
        tuple(GeoErrorCode,
              result 2D polygon of union)
    """
@typing.overload
def MakeUnion(polyhed1: Polyhedron3D, polyhed2: Polyhedron3D) -> tuple[eGeometryErrorCode, Polyhedron3D]:
    """make union of 3D polyhedrons

    Args:
        polyhed1: first polyhedron
        polyhed2: second polyhedron

    Returns:
        tuple(GeoErrorCode,
              result 3D polyhedron of union)
    """
@typing.overload
def MakeUnion(bodies: Polyhedron3DList) -> tuple[bool, Polyhedron3D]:
    """Compute bulk union of more polyhedra at once

    Args:
        bodies: polyhedra to unite

    Returns:
        if success result polyhedron otherwise nullopt
    """
@typing.overload
def MakeUnion(brep1: BRep3D, brep2: BRep3D) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute union of 2 breps

    Args:
        brep1: first brep
        brep2: second brep

    Returns:
        tuple(error code,
              result brep of union)
    """
@typing.overload
def MakeUnion(brep1: BRep3D, breps: BRep3DList) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute union of brep and a list of breps

    Args:
        brep1: first brep
        breps: list of breps

    Returns:
        tuple(error code,
              result brep of union)
    """
@typing.overload
def MakeUnion(breps: BRep3DList) -> tuple[eGeometryErrorCode, BRep3D]:
    """Compute union of more breps at once (using paralelism if possible)

    Args:
        breps: breps to unite

    Returns:
        tuple(error code,
              result brep of union)
    """
def MakeUnion(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def Mirror(point: Point3D, plane: Plane3D) -> Point3D:
    """Mirror point 3D

    Args:
        point: mirroring point
        plane: mirror plane

    Returns:
        mirrored point
    """
@typing.overload
def Mirror(point: Point3D, axis: Axis2D) -> Point3D:
    """2D Mirror of 3D point

    Args:
        point: mirroring point
        axis:  mirror plane

    Returns:
        mirrored point
    """
@typing.overload
def Mirror(vec: Vector3D, plane: Plane3D) -> Vector3D:
    """Mirror vector 3D

    Args:
        vec:   mirroring vector
        plane: mirror plane

    Returns:
        mirrored vector
    """
@typing.overload
def Mirror(vec: Vector3D, axis: Axis2D) -> Vector3D:
    """2D mirror of 3D vector

    Args:
        vec:  mirroring vector
        axis: mirror axis

    Returns:
        mirrored vector
    """
@typing.overload
def Mirror(point: Point2D, plane: Plane3D) -> Point2D:
    """Mirror point 2D

    Args:
        point: mirroring point 2D
        plane: mirror plane

    Returns:
        mirrored point
    """
@typing.overload
def Mirror(point: Point2D, axis: Axis2D) -> Point2D:
    """2D Mirror of 3D point

    Args:
        point: mirroring point 2D
        axis:  mirror axis

    Returns:
        mirrored point
    """
@typing.overload
def Mirror(vec: Vector2D, plane: Plane3D) -> Vector2D:
    """Mirror vector 2D

    Args:
        vec:   mirroring point
        plane: mirror plane

    Returns:
        mirrored vector
    """
@typing.overload
def Mirror(vec: Vector2D, axis: Axis2D) -> Vector2D:
    """2D mirror of 2D vector

    Args:
        vec:  mirroring vector
        axis: mirror axis

    Returns:
        mirrored vector
    """
@typing.overload
def Mirror(line: Line2D, plane: Plane3D) -> Line2D:
    """Mirror line 2D

    Args:
        line:  mirroring line 2D
        plane: mirror plane

    Returns:
        mirrored line
    """
@typing.overload
def Mirror(line: Line2D, axis: Axis2D) -> Line2D:
    """Mirror line 2D

    Args:
        line: mirroring line 2D
        axis: mirror axis

    Returns:
        mirrored line
    """
@typing.overload
def Mirror(line: Line3D, plane: Plane3D) -> Line3D:
    """Mirror line 3D

    Args:
        line:  mirroring line 3D
        plane: mirror plane

    Returns:
        mirrored line
    """
@typing.overload
def Mirror(line: Line3D, axis: Axis2D) -> Line3D:
    """2D mirror of 3D line

    Args:
        line: mirroring line 3D
        axis: mirror axis

    Returns:
        mirrored line
    """
@typing.overload
def Mirror(polyline: Polyline2D, plane: Plane3D) -> Polyline2D:
    """Mirror polyline 2D

    Args:
        polyline: mirroring polyline 2D
        plane:    mirror plane

    Returns:
        mirrored polyline
    """
@typing.overload
def Mirror(polyline: Polyline2D, axis: Axis2D) -> Polyline2D:
    """2D mirror of 2D polyline

    Args:
        polyline: mirroring polyline 2D
        axis:     mirror axis

    Returns:
        mirrored polyline
    """
@typing.overload
def Mirror(polygon: Polygon2D, plane: Plane3D) -> Polygon2D:
    """Mirror polygon 2d

    Args:
        polygon: polygon to mirror
        plane:   mirror plane

    Returns:
        mirrored polygon
    """
@typing.overload
def Mirror(polygon: Polygon2D, axis: Axis2D) -> Polygon2D:
    """Mirror polygon 2d

    Args:
        polygon: polygon to mirror
        axis:    mirror axis

    Returns:
        mirrored polygon
    """
@typing.overload
def Mirror(plane: Plane3D, axis: Axis2D) -> Plane3D:
    """Mirror plane

    Args:
        plane: plane to mirror
        axis:  mirror axis

    Returns:
        mirrored polygonal area
    """
@typing.overload
def Mirror(pla: Plane3D, plane: Plane3D) -> Plane3D:
    """Mirror plane

    Args:
        pla:   plane to mirror
        plane: mirror plane

    Returns:
        mirrored polygonal area
    """
@typing.overload
def Mirror(polygon: PolygonalArea2D, axis: Axis2D) -> PolygonalArea2D:
    """Mirror polygonal area 2D

    Args:
        polygon: polygon to mirror
        axis:    mirror axis

    Returns:
        mirrored polygonal area
    """
@typing.overload
def Mirror(polygon: PolygonalArea3D, axis: Axis2D) -> PolygonalArea3D:
    """Mirror polygonal area 2D

    Args:
        polygon: polygon to mirror
        axis:    mirror axis

    Returns:
        mirrored polygonal area
    """
@typing.overload
def Mirror(polygon: PolygonalArea3D, plane: Plane3D) -> PolygonalArea3D:
    """Mirror polygonal area 3D

    Args:
        polygon: polygon to mirror
        plane:   mirror plane

    Returns:
        mirrored polygonal area
    """
@typing.overload
def Mirror(polyline: Polyline3D, plane: Plane3D) -> Polyline3D:
    """Mirror polyline 3D

    Args:
        polyline: mirroring polyline 3D
        plane:    mirror plane

    Returns:
        mirrored polyline
    """
@typing.overload
def Mirror(polyline: Polyline3D, axis: Axis2D) -> Polyline3D:
    """Mirror polyline 3D

    Args:
        polyline: mirroring polyline 3D
        axis:     mirror axis

    Returns:
        mirrored polyline
    """
@typing.overload
def Mirror(polygon: Polygon3D, plane: Plane3D) -> Polygon3D:
    """Mirror polygon 3D

    Args:
        polygon: mirroring polygon 3D
        plane:   mirror plane

    Returns:
        mirrored polygon
    """
@typing.overload
def Mirror(polygon: Polygon3D, axis: Axis2D) -> Polygon3D:
    """Mirror polygon 3D

    Args:
        polygon: mirroring polygon 3D
        axis:    mirror axis

    Returns:
        mirrored polygon
    """
@typing.overload
def Mirror(spline: Spline2D, plane: Plane3D) -> Spline2D:
    """Mirror spline 2D

    Args:
        spline: mirroring spline 2D
        plane:  mirror plane

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(spline: Spline2D, axis: Axis2D) -> Spline2D:
    """Mirror spline 2D

    Args:
        spline: mirroring spline 2D
        axis:   mirror axis

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(spline: Spline3D, plane: Plane3D) -> Spline3D:
    """Mirror spline 3D

    Args:
        spline: mirroring spline 3D
        plane:  mirror plane

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(spline: Spline3D, axis: Axis2D) -> Spline3D:
    """Mirror spline 3D

    Args:
        spline: mirroring spline 3D
        axis:   mirror axis

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(bSpline: BSpline2D, plane: Plane3D) -> BSpline2D:
    """Mirror BSpline 2D

    Args:
        bSpline: mirroring bSpline 2D
        plane:   mirror plane

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(bSpline: BSpline2D, axis: Axis2D) -> BSpline2D:
    """Mirror BSpline 2D

    Args:
        bSpline: mirroring bSpline 2D
        axis:    mirror axis

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(bSpline: BSpline3D, plane: Plane3D) -> BSpline3D:
    """Mirror BSpline 3D

    Args:
        bSpline: mirroring bSpline 3D
        plane:   mirror plane

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(bSpline: BSpline3D, axis: Axis2D) -> BSpline3D:
    """Mirror BSpline 3D

    Args:
        bSpline: mirroring bSpline 3D
        axis:    mirror axis

    Returns:
        mirrored spline
    """
@typing.overload
def Mirror(arc: Arc2D, plane: Plane3D) -> Arc2D:
    """Mirror arc 2D

    Args:
        arc:   mirroring arc 2D
        plane: mirror plane

    Returns:
        mirrored arc
    """
@typing.overload
def Mirror(arc: Arc2D, axis: Axis2D) -> Arc2D:
    """Mirror arc 2D

    Args:
        arc:  mirroring arc 2D
        axis: mirror axis

    Returns:
        mirrored arc
    """
@typing.overload
def Mirror(arc: Arc3D, plane: Plane3D) -> Arc3D:
    """Mirror arc 3D

    Args:
        arc:   mirroring arc 3D
        plane: mirror plane

    Returns:
        mirrored arc
    """
@typing.overload
def Mirror(arc: Arc3D, axis: Axis2D) -> Arc3D:
    """Mirror arc 3D

    Args:
        arc:  mirroring arc 3D
        axis: mirror axis

    Returns:
        mirrored arc
    """
@typing.overload
def Mirror(path: Path3D, plane: Plane3D) -> Path3D:
    """Mirror path 3D

    Args:
        path:  mirroring path 3D
        plane: mirror plane

    Returns:
        mirrored path
    """
@typing.overload
def Mirror(path: Path3D, axis: Axis2D) -> Path3D:
    """Mirror path 3D

    Args:
        path: mirroring path 3D
        axis: mirror axis

    Returns:
        mirrored path
    """
@typing.overload
def Mirror(path: Path2D, plane: Plane3D) -> Path2D:
    """Mirror path 2D

    Args:
        path:  mirroring path 2D
        plane: mirror plane

    Returns:
        mirrored path
    """
@typing.overload
def Mirror(path: Path2D, axis: Axis2D) -> Path2D:
    """Mirror path 2D

    Args:
        path: mirroring path 2D
        axis: mirror axis

    Returns:
        mirrored path
    """
@typing.overload
def Mirror(area: ClosedArea2D, plane: Plane3D) -> ClosedArea2D:
    """Mirror path bounded area 2D

    Args:
        area:  mirroring path bounded area 2D
        plane: mirror plane

    Returns:
        mirrored path bounded area
    """
@typing.overload
def Mirror(area: ClosedArea2D, axis: Axis2D) -> ClosedArea2D:
    """Mirror path bounded area 2D

    Args:
        area: mirroring path bounded area 2D
        axis: mirror axis

    Returns:
        mirrored path bounded area
    """
@typing.overload
def Mirror(area: ClosedAreaComposite2D, plane: Plane3D) -> ClosedAreaComposite2D:
    """Mirror path bounded area composite 2D

    Args:
        area:  mirroring path bounded area composite 2D
        plane: mirror plane

    Returns:
        mirrored path bounded area composite
    """
@typing.overload
def Mirror(area: ClosedAreaComposite2D, axis: Axis2D) -> ClosedAreaComposite2D:
    """Mirror path bounded area composite 2D

    Args:
        area: mirroring path bounded area composite 2D
        axis: mirror axis

    Returns:
        mirrored path bounded area composite
    """
@typing.overload
def Mirror(angle: Angle, plane: Plane3D) -> Angle:
    """Mirror angle

    Args:
        angle: mirroring angle
        plane: mirror plane

    Returns:
        mirrored angle
    """
@typing.overload
def Mirror(angle: Angle, axis: Axis2D) -> Angle:
    """Mirror angle

    Args:
        angle: mirroring angle
        axis:  mirror axis

    Returns:
        mirrored angle
    """
@typing.overload
def Mirror(polyhedron: Polyhedron3D, plane: Plane3D) -> Polyhedron3D:
    """Mirror Polyhedron3D

    Args:
        polyhedron: mirroring polyhedron
        plane:      mirror plane

    Returns:
        mirrored polyhedron
    """
@typing.overload
def Mirror(polyhedron: Polyhedron3D, axis: Axis2D) -> Polyhedron3D:
    """2D mirror of 3D Polyhedron

    Args:
        polyhedron: mirroring polyhedron
        axis:       mirror axis

    Returns:
        mirrored polyhedron
    """
@typing.overload
def Mirror(solid: ClippedSweptSolid3D, axis: Axis2D) -> ClippedSweptSolid3D:
    """2D Mirror ClippedSweptSolid3D

    Args:
        solid: solid to mirror
        axis:  mirror axis

    Returns:
        mirrored solid
    """
@typing.overload
def Mirror(solid: ExtrudedAreaSolid3D, plane: Plane3D) -> ExtrudedAreaSolid3D:
    """Mirror ExtrudedAreaSolid3D

    Args:
        solid: solid to mirror
        plane: mirror plane

    Returns:
        mirrored solid
    """
@typing.overload
def Mirror(solid: ExtrudedAreaSolid3D, axis: Axis2D) -> ExtrudedAreaSolid3D:
    """2D Mirror of ExtrudedAreaSolid3D

    Args:
        solid: solid to mirror
        axis:  mirror axis

    Returns:
        mirrored solid
    """
@typing.overload
def Mirror(clothoid: Clothoid2D, plane: Plane3D) -> Clothoid2D:
    """Mirror of Clothoid2D

    Args:
        clothoid: clothoid to mirror
        plane:    mirror plane

    Returns:
        mirrored solid
    """
@typing.overload
def Mirror(clothoid: Clothoid2D, axis: Axis2D) -> Clothoid2D:
    """2D Mirror of Clothoid2D

    Args:
        clothoid: clothoid to mirror
        axis:     mirror axis

    Returns:
        mirrored solid
    """
@typing.overload
def Mirror(placement: AxisPlacement2D, axis: Axis2D) -> AxisPlacement2D:
    """2D Mirror AxisPlacement2D

    Args:
        placement: axis placement to mirror
        axis:      mirror axis

    Returns:
        mirrored placement
    """
@typing.overload
def Mirror(placement: AxisPlacement2D, plane: Plane3D) -> AxisPlacement2D:
    """3D Mirror AxisPlacement2D

    Args:
        placement: axis placement to mirror
        plane:     mirror plane

    Returns:
        mirrored placement
    """
@typing.overload
def Mirror(placement: AxisPlacement3D, axis: Axis2D) -> AxisPlacement3D:
    """2D Mirror AxisPlacement3D

    Args:
        placement: axis placement to mirror
        axis:      mirror axis

    Returns:
        mirrored placement
    """
@typing.overload
def Mirror(placement: AxisPlacement3D, plane: Plane3D) -> AxisPlacement3D:
    """3D Mirror AxisPlacement3D

    Args:
        placement: axis placement to mirror
        plane:     mirror plane

    Returns:
        mirrored placement
    """
@typing.overload
def Mirror(cylinder: Cylinder3D, plane: Plane3D) -> Cylinder3D:
    """Mirror Cylinder3D

    Args:
        cylinder: Cylinder to mirror
        plane:    mirror plane

    Returns:
        mirrored cylinder
    """
@typing.overload
def Mirror(cylinder: Cylinder3D, axis: Axis2D) -> Cylinder3D:
    """Mirror Cylinder3D

    Args:
        cylinder: Cylinder to mirror
        axis:     mirror axis

    Returns:
        mirrored cylinder
    """
@typing.overload
def Mirror(cone: Cone3D, plane: Plane3D) -> Cone3D:
    """Mirror Cone3D

    Args:
        cone:  Cone to mirror
        plane: mirror plane

    Returns:
        mirrored Cone
    """
@typing.overload
def Mirror(cone: Cone3D, axis: Axis2D) -> Cone3D:
    """Mirror Cone3D

    Args:
        cone: Cone to mirror
        axis: mirror axis

    Returns:
        mirrored Cone
    """
@typing.overload
def Mirror(ellipsoid: Ellipsoid3D, plane: Plane3D) -> Ellipsoid3D:
    """Mirror Ellipsoid3D

    Args:
        ellipsoid: Ellipsoid to mirror
        plane:     mirror plane

    Returns:
        mirrored Ellipsoid
    """
@typing.overload
def Mirror(ellipsoid: Ellipsoid3D, axis: Axis2D) -> Ellipsoid3D:
    """Mirror Ellipsoid3D

    Args:
        ellipsoid: Ellipsoid to mirror
        axis:      mirror axis

    Returns:
        mirrored Ellipsoid
    """
@typing.overload
def Mirror(brep: BRep3D, plane: Plane3D) -> BRep3D:
    """3D Mirror brep3D

    Args:
        brep:  brep
        plane: mirror plane

    Returns:
        mirrored placement
    """
def Mirror(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def Move(box: BoundingBox2D, translation: Vector2D) -> BoundingBox2D:
    """Move bounding box

    Args:
        box:         Moving bounding box
        translation: Vector of translation

    Returns:
        Moved bounding box
    """
@typing.overload
def Move(area: PolygonalArea2D, translation: Vector2D) -> PolygonalArea2D:
    """Move polygonal area

    Args:
        area:        PolygonalArea2D to move
        translation: Vector of translation

    Returns:
        PolygonalArea2D Moved area
    """
@typing.overload
def Move(plane: Plane3D, translation: Vector3D) -> Plane3D:
    """Move plane

    Args:
        plane:       Plane3D to move
        translation: Vector of translation

    Returns:
        Plane3D Moved plane
    """
@typing.overload
def Move(arc2D: Arc2D, moveVector: Vector2D) -> Arc2D:
    """Move Arc2D by given vector

    Args:
        arc2D:      Arc2D to move
        moveVector: Vector of translation

    Returns:
        Arc2D      Moved arc
    """
@typing.overload
def Move(arc3D: Arc3D, moveVector: Vector3D) -> Arc3D:
    """Move Arc3D by given vector

    Args:
        arc3D:     Arc3D to move
        moveVector: Vector of translation

    Returns:
        Arc3D      Moved Arc
    """
@typing.overload
def Move(axis2D: Axis2D, moveVector: Vector2D) -> Axis2D:
    """Move Axis2D by given vector

    Args:
        axis2D:     Axis2D to move
        moveVector: Vector of translation

    Returns:
        Axis2D      Moved Axis
    """
@typing.overload
def Move(axis3D: Axis3D, moveVector: Vector3D) -> Axis3D:
    """Move Axis3D by given vector

    Args:
        axis3D:     Axis3D to move
        moveVector: Vector of translation

    Returns:
        Axis3D      Moved axis
    """
@typing.overload
def Move(axisPlacement2D: AxisPlacement2D, moveVector: Vector2D) -> AxisPlacement2D:
    """Move AxisPlacement2D by given vector

    Args:
        axisPlacement2D: AxisPlacement2D to move
        moveVector:      Vector of translation

    Returns:
        AxisPlacement2D     Moved axis placement
    """
@typing.overload
def Move(axisPlacement3D: AxisPlacement3D, moveVector: Vector3D) -> AxisPlacement3D:
    """Move AxisPlacement3D by given vector

    Args:
        axisPlacement3D: AxisPlacement3D to move
        moveVector:      Vector of translation

    Returns:
        AxisPlacement3D     Moved placement
    """
@typing.overload
def Move(clippedSweptSolid3D: ClippedSweptSolid3D, vec: Vector3D) -> ClippedSweptSolid3D:
    """Move ClippedSweptSolid3D by given vector

    Args:
        clippedSweptSolid3D: ClippedSweptSolid3D to move
        vec:                 Vector of translation

    Returns:
        ClippedSweptSolid3D     Moved solid
    """
@typing.overload
def Move(clothoid2D: Clothoid2D, moveVector: Vector2D) -> Clothoid2D:
    """Move Clothoid2D by given vector

    Args:
        clothoid2D: Clothoid2D to move
        moveVector: Vector of translation

    Returns:
        Clothoid2D      Moved clothoid
    """
@typing.overload
def Move(cuboid3D: Cuboid3D, moveVector: Vector3D) -> Cuboid3D:
    """Move Cuboid3D by given vector

    Args:
        cuboid3D:   Cuboid3D to move
        moveVector: Vector of translation

    Returns:
        Cuboid3D    Moved cuboid
    """
@typing.overload
def Move(extrudedAreaSolid3D: ExtrudedAreaSolid3D, moveVector: Vector3D) -> ExtrudedAreaSolid3D:
    """Move ExtrudedAreaSolid3D by given vector

    Args:
        extrudedAreaSolid3D: ExtrudedAreaSolid3D to move
        moveVector:          Vector of translation

    Returns:
        ExtrudedAreaSolid3D     Moved solid
    """
@typing.overload
def Move(line2D: Line2D, moveVector: Vector2D) -> Line2D:
    """Move Line2D by given vector

    Args:
        line2D:     Line2D to move
        moveVector: Vector of translation

    Returns:
        Line2D      Moved line
    """
@typing.overload
def Move(line3D: Line3D, moveVector: Vector3D) -> Line3D:
    """Move Line3D by given vector

    Args:
        line3D:     Line3D to move
        moveVector: Vector of translation

    Returns:
        Line3D      Moved line
    """
@typing.overload
def Move(path2D: Path2D, moveVector: Vector2D) -> Path2D:
    """Move Path2D by given vector

    Args:
        path2D:     Path2D to move
        moveVector: Vector of translation

    Returns:
        Path2D      Moved path
    """
@typing.overload
def Move(path3D: Path3D, moveVector: Vector3D) -> Path3D:
    """Move Path3D by given vector

    Args:
        path3D:     Path3D to move
        moveVector: Vector of translation

    Returns:
        Path3D      Moved path
    """
@typing.overload
def Move(point2D: Point2D, moveVector: Vector2D) -> Point2D:
    """Move Point2D by given vector

    Args:
        point2D:    Point2D to move
        moveVector: Vector of translation

    Returns:
        Point2D    Moved point
    """
@typing.overload
def Move(point3D: Point3D, moveVector: Vector3D) -> Point3D:
    """Move Point3D by given vector

    Args:
        point3D:    Point3D to move
        moveVector: Vector of translation

    Returns:
        Point3D     Moved point
    """
@typing.overload
def Move(polygon2D: Polygon2D, moveVector: Vector2D) -> Polygon2D:
    """Move Polygon2D by given vector

    Args:
        polygon2D:  Polygon2D to move
        moveVector: Vector of translation

    Returns:
        Polygon2D   Moved polygon
    """
@typing.overload
def Move(polygon3D: Polygon3D, moveVector: Vector3D) -> Polygon3D:
    """Move Polygon3D by given vector

    Args:
        polygon3D:  Polygon3D to move
        moveVector: Vector of translation

    Returns:
        Polygon3D   Moved polygon
    """
@typing.overload
def Move(polygonalArea3D: PolygonalArea3D, moveVector: Vector3D) -> PolygonalArea3D:
    """Move PolygonalArea3D by given vector

    Args:
        polygonalArea3D: PolygonalArea3D to move
        moveVector:      Vector of translation

    Returns:
        PolygonalArea3D   Moved polygonal area
    """
@typing.overload
def Move(polyhedron3D: Polyhedron3D, moveVector: Vector3D) -> Polyhedron3D:
    """Move Polyhedron3D by given vector

    Throw exception in case of error

    Args:
        polyhedron3D: Polyhedron3D to move
        moveVector:   Vector of translation

    Returns:
        Polyhedron3D    Moved polyhedron
    """
@typing.overload
def Move(polyline2D: Polyline2D, moveVector: Vector2D) -> Polyline2D:
    """Move Polyline2D by given vector

    Args:
        polyline2D: Polyline2D to move
        moveVector: Vector of translation

    Returns:
        Polyline2D   Moved polyline
    """
@typing.overload
def Move(polyline3D: Polyline3D, moveVector: Vector3D) -> Polyline3D:
    """Move Polyline3D by given vector

    Args:
        polyline3D: Polyline3D to move
        moveVector: Vector of translation

    Returns:
        Polyline3D   Moved polyline
    """
@typing.overload
def Move(area: ClosedArea2D, moveVector: Vector2D) -> ClosedArea2D:
    """Move ClosedArea2D by given vector

    Args:
        area:       ClosedArea2D to move
        moveVector: Vector of translation

    Returns:
        ClosedArea2D   Moved area
    """
@typing.overload
def Move(area: ClosedAreaComposite2D, moveVector: Vector2D) -> ClosedAreaComposite2D:
    """Move ClosedAreaComposite2D by given vector

    Args:
        area:       ClosedAreaComposite2D to move
        moveVector: Vector of translation

    Returns:
        ClosedAreaComposite2D    Moved area composite
    """
@typing.overload
def Move(cylinder3D: Cylinder3D, moveVector: Vector3D) -> Cylinder3D:
    """Move Cylinder3D by given vector

    Args:
        cylinder3D: Cylinder3D to move
        moveVector: Vector of translation

    Returns:
        Cylinder3D   Moved Cylinder
    """
@typing.overload
def Move(ellipsoid3D: Ellipsoid3D, moveVector: Vector3D) -> Ellipsoid3D:
    """Move Ellipsoid3D by given vector

    Args:
        ellipsoid3D: Ellipsoid3D to move
        moveVector:  Vector of translation

    Returns:
        Ellipsoid3D  Moved Ellipsoid3D
    """
@typing.overload
def Move(cone3D: Cone3D, moveVector: Vector3D) -> Cone3D:
    """Move Cone3D by given vector

    Args:
        cone3D:     Cone3D to move
        moveVector: Vector of translation

    Returns:
        Cone3D       Moved Cone
    """
@typing.overload
def Move(spline2D: Spline2D, moveVector: Vector2D) -> Spline2D:
    """Move Spline2D by given vector

    Args:
        spline2D:   Spline2D to move
        moveVector: Vector of translation

    Returns:
        Spline2D    Moved spline
    """
@typing.overload
def Move(spline3D: Spline3D, moveVector: Vector3D) -> Spline3D:
    """Move Spline3D by given vector

    Args:
        spline3D:   Spline3D to move
        moveVector: Vector of translation

    Returns:
        Spline3D    Moved spline
    """
@typing.overload
def Move(bspline3D: BSpline3D, moveVector: Vector3D) -> BSpline3D:
    """Move BSpline3D by given vector

    Args:
        bspline3D:  BSpline3D to move
        moveVector: Vector of translation

    Returns:
        BSpline3D   Moved spline
    """
@typing.overload
def Move(brep: BRep3D, moveVector: Vector3D) -> BRep3D:
    """Move BRep3D by given vector

    Args:
        brep:       BRep3D to move
        moveVector: Vector of translation

    Returns:
        BRep3D   Moved spline
    """
def Move(self):
    """ Overloaded function. See individual overloads.
    """
def MoveArc3DToZ0Plane(arc3D: Arc3D) -> tuple[NemAll_Python_GeometryeServiceResult, Arc2D]:
    """Move the given 3D arc on the z = 0 plane and create a 2D fromn it

    Args:
        arc3D: Arc 3D

    Returns:
        tuple(NO_ERR or INVALID_GEOOBJECT,
              Arc 2D)
    """
def MoveSpline3DToZ0Plane(spline3D: Spline3D) -> tuple[NemAll_Python_GeometryeServiceResult, Spline2D]:
    """Move the given 3D arc on the z = 0 plane and create a 2D from it

    Args:
        spline3D: Spline 3D

    Returns:
        tuple(NO_ERR or INVALID_GEOOBJECT,
              Spline 2D)
    """
@typing.overload
def Offset(rDistance: float, geoObjects: list, checkSegmentsOrientation: bool) -> eGeometryErrorCode:
    """Counts parallel for Chain

    If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        rDistance:                Distances for the Chain
        geoObjects:               Source elements and destination elements
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        eGeometryErrorCode
    """
@typing.overload
def Offset(srcElement: object, distance: float) -> tuple[eGeometryErrorCode, typingAny]:
    """Create a parallel element from the given distance

    Args:
        srcElement: Source element
        distance:   Distances for the points

    Returns:
        tuple(A parallel element,
              Parallel element)
    """
@typing.overload
def Offset(point: Point2D, lineSrc: Line2D) -> tuple[eGeometryErrorCode, Line2D]:
    """Counts parallel to 2D-Line

    Args:
        point:   Parallel to this point
        lineSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element to the source through the "point")
    """
@typing.overload
def Offset(dist: float, lineSrc: Line2D) -> tuple[eGeometryErrorCode, Line2D]:
    """Counts parallel to 2D-Line

    Args:
        dist:    Distance from the source
        lineSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element to the source through the "point")
    """
@typing.overload
def Offset(point: Point2D, pathSrc: Path2D) -> tuple[eGeometryErrorCode, Path2D]:
    """Calculate parallel to Path2D

    Args:
        point:   parallel defined by the point
        pathSrc: source path

    Returns:
        tuple(GeoErrorCode,
              destination parallel path)
    """
@typing.overload
def Offset(dist: float, pathSrc: Path2D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Path2D]:
    """Calculate parallel to Path2D
                 If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        dist:                     parallel defined by distance
        pathSrc:                  source path
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(GeoErrorCode,
              destination path)
    """
@typing.overload
def Offset(point: Point3D, dist: float, lineSrc: Line3D, offsetPlane: Offset3DPlane) -> tuple[eGeometryErrorCode, Line3D]:
    """Counts parallel to 3D-Line

    If the "dist" value is zero, the "point" arg is used as a base to parallel.
    In other case, the "dist" would be the distance from the source and the point represents the orientation.

    Args:
        point:       Parallel to this point
        dist:        Distance from the source
        lineSrc:     Source element
        offsetPlane: Plane on which parallel line will be calculated

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, offsetPlane: Plane3D, parallelsCount: int, polySrc: Polyline3D) -> tuple[eGeometryErrorCode, Polyline3DList]:
    """Counts parallels to 3D Polyline

    Args:
        dist:           Distance from the source
        offsetPlane:    Plane on which offsets will be calculated
        parallelsCount: Count of parallels to calculate
        polySrc:        Source element

    Returns:
        tuple(eOK if successful,
              Parallel elements)
    """
@typing.overload
def Offset(point: Point3D, offsetPlane: Plane3D, parallelsCount: int, polySrc: Polyline3D) -> tuple[eGeometryErrorCode, Polyline3DList]:
    """Counts parallels to 3D Polyline

    Args:
        point:          Parallel to this point
        offsetPlane:    Plane on which offsets will be calculated
        parallelsCount: Count of parallels to calculate
        polySrc:        Source element

    Returns:
        tuple(eOK if successful,
              Parallel elements)
    """
@typing.overload
def Offset(point: Point3D, arc3DSrc: Arc3D) -> tuple[eGeometryErrorCode, Arc3D]:
    """Counts parallel to Arc3D

    Args:
        point:    Parallel to this point
        arc3DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, arc3DSrc: Arc3D) -> tuple[eGeometryErrorCode, Arc3D]:
    """Counts parallel to Arc3D

    Args:
        dist:     Distance from the source
        arc3DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(point: Point2D, arc2DSrc: Arc2D) -> tuple[eGeometryErrorCode, Arc2D]:
    """Counts parallel to Arc2D

    Args:
        point:    Parallel to this point
        arc2DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, arc2DSrc: Arc2D) -> tuple[eGeometryErrorCode, Arc2D]:
    """Counts parallel to Arc2D

    Args:
        dist:     Distance from the source
        arc2DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, spline2DSrc: Spline2D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Spline2D]:
    """Counts parallel to Spline2D

    If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        dist:                     Distance from the source
        spline2DSrc:              Source element
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, spline3DSrc: Spline3D, plane: Plane3D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Spline3D]:
    """Calculates parallel to Spline3D - only for planar 3D splines !!!

    If checkSegmentsOrientation is true, new spline must have same count of points as original

    Args:
        dist:                     Distance from the source
        spline3DSrc:              Source element
        plane:                    plane to offset in
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(point: Point2D, spline2DSrc: Spline2D) -> tuple[eGeometryErrorCode, Spline2D]:
    """Counts parallel to Spline2D

    Args:
        point:       Parallel to this point
        spline2DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(point: Point3D, spline3DSrc: Spline3D, plane: Plane3D) -> tuple[eGeometryErrorCode, Spline3D]:
    """Calculates parallel to Spline3D - only for planar 3D splines !!!

    Args:
        point:       Parallel to this point
        spline3DSrc: Source element
        plane:       plane to offset in

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(dist: float, spline2DSrc: Spline2D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Polyline2D]:
    """Counts parallel to Spline2D

    If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        dist:                     Distance from the source
        spline2DSrc:              Source element
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(eOK if successful,
              Parallel element as a Polyline2D)
    """
@typing.overload
def Offset(dist: float, clothoid2DSrc: Clothoid2D) -> tuple[eGeometryErrorCode, Clothoid2D]:
    """Count parallel to Clothoid2D

    Args:
        dist:          Distance from the source
        clothoid2DSrc: Source element

    Returns:
        tuple(Return eOK if successful, otherwise return error code,
              Parallel element to source)
    """
@typing.overload
def Offset(point: Point2D, clothoid2DSrc: Clothoid2D) -> tuple[eGeometryErrorCode, Clothoid2D]:
    """Count parallel to Clothoid2D

    Args:
        point:         Parallel to this point
        clothoid2DSrc: Source element

    Returns:
        tuple(Return eOK if successful, otherwise return error code,
              Parallel element to source)
    """
@typing.overload
def Offset(rDistance: float, polyline2D: Polyline2D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Polyline2D]:
    """Counts parallel to Polyline2D

    If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        rDistance:                Distance from the source
        polyline2D:               Source element
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(point: Point2D, polyline2DSrc: Polyline2D) -> tuple[eGeometryErrorCode, Polyline2D]:
    """Counts parallel to Polyline2D

    Args:
        point:         Parallel to this point
        polyline2DSrc: Source element

    Returns:
        tuple(eOK if successful,
              Parallel element)
    """
@typing.overload
def Offset(rDistance: float, polygon: Polygon2D, checkSegmentsOrientation: bool) -> tuple[eGeometryErrorCode, Polygon2D]:
    """Calculate parallel polygon
                 If checkSegmentsOrientation is true, new polyline must have same count of points as original

    Args:
        rDistance:                input polygon
        polygon:                  offset value
        checkSegmentsOrientation: check, if segments in parallel geometry has same orientation as in original

    Returns:
        tuple(eOK if successful,
              result polygon)
    """
@typing.overload
def Offset(distances: NemAll_Python_Utility.VecDoubleList, polyline: Polyline2D) -> Polyline2D:
    """Create a parallel line from distances

    Args:
        distances: Distances for the points
        polyline:  Source element

    Returns:
        A parallel polyline
    """
@typing.overload
def Offset(inputPath: Path3D, normVector: Vector3D, offsetDistance: float) -> tuple[eGeometryErrorCode, Path3D]:
    """Create offset of Path3D

    Args:
        inputPath:      input path
        normVector:     normal vector of plane in that the offset will be calculated
        offsetDistance: offset distance

    Returns:
        tuple(error code,
              result offset curve)
    """
@typing.overload
def Offset(inputPath: Path3D, inputPoint: Point3D, rayVector: Vector3D, plane: Plane3D) -> tuple[eGeometryErrorCode, Path3D]:
    """Offset Path3D  in distance given with cursor point

    Args:
        inputPath:  input path
        inputPoint: cursor point (ray point)
        rayVector:  ray vector
        plane:      plane of the planar face (of given boundary curves)

    Returns:
        tuple(error code,
              result path)
    """
def Offset(self):
    """ Overloaded function. See individual overloads.
    """
def OffsetCurve(inputCurves: Curve3DList, normVector: Vector3D, offsetDistance: float, sortEdges: bool = False) -> tuple:
    """Offset 3D curves with given distance

    Args:
        inputCurves:    input curves
        normVector:     normal vector of plane in that the offset will be calculated
        offsetDistance: offset distance
        sortEdges:      flag if to sort edges to original order

    Returns:
        tuple(error code,
              result offset curves)
    """
@typing.overload
def Polygonize(geometry_object: object, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float) -> tuple[bool, Polyline3D]:
    """Polygonize whole curve

    Args:
        geometry_object:    Geometry object which will be polygonized
        arcSegmentation:    segment number
        useArcSegmentation: if use segment polygonization, set to 0
        armLength:          max length of calculated segment, for rise value polygonization only
        riseValue:          rise value

    Returns:
        tuple(bool true = success,
              result polyline)
    """
@typing.overload
def Polygonize(geometry_object: object, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int,
               armLength: float, riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        geometry_object:    Geometry object which will be polygonized
        fromPoint:          where to begin the polygonization; The point has to be on one of the Objects
        toPoint:            where to end the polygonization; The point has to be on one of the Objects
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(path: Path2D, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonizes multiple geometry objects, if they if they follow directly one another

    emark The objects in the path must follow directly one another. This means, the start- or endpoint
            of one object has to be the start- or endpoint of the next object in the path and the other point
            of the object has to be the start- or endpoint of the previous object in the path.
            eg.: Start1-End1, End2-Start2, End3-Start3, Start4-End4 and so on.
            where, End1 == End2, Start2 == End3, Start3 == Start4

            If they don't follow one another, it's unknown how the calculated polyline will look.

            The parameters: arcSegmentation, useArcSegmentation, armLength, riseValue are not relevant for lines and polylines.
            eps is only relevant if, there is a spline or clothoid in the vector.
            See class-description for more information about these parameters.

    Args:
        path:               The vector with the objects, which will be polygonized
        fromPoint:          where to begin the polygonization; The point has to be on one of the Objects
        toPoint:            where to end the polygonization; The point has to be on one of the Objects
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(line: Line2D, fromPoint: Point3D, toPoint: Point3D, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        line:      Line which will be polygonized
        fromPoint: where to begin the polygonization; The point has to be on one of the Objects
        toPoint:   where to end the polygonization; The point has to be on one of the Objects
        eps:       stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(polyline: Polyline2D, fromPoint: Point3D, toPoint: Point3D, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        polyline:  Polyline which will be polygonized
        fromPoint: where to begin the polygonization; The point has to be on one of the Objects
        toPoint:   where to end the polygonization; The point has to be on one of the Objects
        eps:       stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(polygon: Polygon2D, fromPoint: Point3D, toPoint: Point3D, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        polygon:   Polygon which will be polygonized
        fromPoint: where to begin the polygonization; The point has to be on one of the Objects
        toPoint:   where to end the polygonization; The point has to be on one of the Objects
        eps:       stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(arc: Arc2D, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        arc:                Arc which will be polygonized
        fromPoint:          where to begin the polygonization; The point has to be on one of the Objects
        toPoint:            where to end the polygonization; The point has to be on one of the Objects
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(arc: Arc2D, fromPoint: Point2D, toPoint: Point2D, count: int, bInscribed: bool) -> tuple[bool, Polyline2D]:
    """Polygonize Arc2D with given division

    Args:
        arc:        Arc2D
        fromPoint:  Start point for polygonization
        toPoint:    End point for polygonization
        count:      Count of segments
        bInscribed: in case of inscribed circle there is additional segment (one segment divided to 2 parts)

    Returns:
        tuple(bool (true = polygonization possible),
              PolyLine2D)
    """
@typing.overload
def Polygonize(arc: Arc2D, countOfSegments: int) -> Polyline2D:
    """Polygonize a Arc2D geometry object

    Args:
        arc:             Arc2D which will be polygonized
        countOfSegments: Count of segments

    Returns:
        Polyline2D      The polyline will be filled with the points of the polygonization
    """
@typing.overload
def Polygonize(spline: Spline2D, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        spline:             Spline which will be polygonized
        fromPoint:          where to begin the polygonization; The point has to be on one of the Objects
        toPoint:            where to end the polygonization; The point has to be on one of the Objects
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(bspline: BSpline2D, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int,
               armLength: float, riseValue: float) -> tuple[bool, Polyline2D]:
    """Polygonize a BSpline2D geometry object

    Args:
        bspline:            BSpline2D which will be polygonized
        fromPoint:          where to begin the polygonization
        toPoint:            where to end the polygonization
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(clothoid: Clothoid2D, fromPoint: Point3D, toPoint: Point3D, arcSegmentation: int, useArcSegmentation: int,
               armLength: float, riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object

    Args:
        clothoid:           Clothoid which will be polygonized
        fromPoint:          where to begin the polygonization; The point has to be on one of the Objects
        toPoint:            where to end the polygonization; The point has to be on one of the Objects
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(arc: Arc3D, countOfSegments: int) -> Polyline3D:
    """Polygonize a Arc3D geometry object

    Args:
        arc:             Arc3D which will be polygonized
        countOfSegments: Count of segments

    Returns:
        Polyline3D          the polyline will be filled with the points of the polygonization
    """
@typing.overload
def Polygonize(arc: Arc3D, arcSegmentation: int, useArcSegmentation: int, armLength: float, riseValue: float) -> tuple[bool,
               Polyline3D]:
    """Polygonize a Arc3D geometry object

    Args:
        arc:                Arc3D which will be polygonized
        arcSegmentation:    Count of segments
        useArcSegmentation: if use segment polygonization, set to 0
        armLength:          max length of calculated segment, for rise value polygonization only
        riseValue:          rise value

    Returns:
        tuple(bool true = success,
              result polyline)
    """
@typing.overload
def Polygonize(path: Path3D, countOfSegments: int) -> Polyline3D:
    """Polygonize a Path3D geometry object

    Args:
        path:            Path3D which will be polygonized
        countOfSegments: Count of segments

    Returns:
        Polyline3D          the polyline will be filled with non repeated points of the polygonization
    """
@typing.overload
def Polygonize(path: Path3D, arcSegmentation: int, useArcSegmentation: int, armLength: float, riseValue: float) -> Polyline3D:
    """Polygonize a Arc3D geometry object

    Args:
        path:               Path3D which will be polygonized
        arcSegmentation:    Count of segments
        useArcSegmentation: if use segment polygonization, set to 0
        armLength:          max length of calculated segment, for rise value polygonization only
        riseValue:          rise value

    Returns:
        the result polyline
    """
@typing.overload
def Polygonize(spline: Spline3D, linesPerSegment: int) -> Polyline3D:
    """Polygonize a Spline3D geometry object

    Args:
        spline:          Spline3D which will be polygonized
        linesPerSegment: Count of lines per segment

    Returns:
        Polyline3D          the polyline will be filled with the points of the polygonization
    """
@typing.overload
def Polygonize(spline: Spline3D, minmaxRadius: float, pixelSize: float) -> tuple[bool, Polyline3D]:
    """Polygonize Spline3D

    Args:
        spline:       Spline3D
        minmaxRadius: radius of minmax
        pixelSize:    size of pixel

    Returns:
        tuple(bool (true = polygonization possible),
              polygonized spline)
    """
@typing.overload
def Polygonize(spline: BSpline3D, arcSegmentation: int, useArcSegmentation: int, armLength: float, riseValue: float) -> tuple[bool,
               Polyline3D]:
    """Polygonize B-spline curve

    Args:
        spline:             spline to tesselate
        arcSegmentation:    segment number
        useArcSegmentation: if use segment polygonization, set to 0
        armLength:          max length of calculated segment, for rise value polygonization only
        riseValue:          rise value

    Returns:
        tuple(bool true = success,
              result polyline)
    """
@typing.overload
def Polygonize(spline: Spline3D, arcSegmentation: int, useArcSegmentation: int, armLength: float, riseValue: float) -> tuple[bool,
               Polyline3D]:
    """Polygonize whole spline curve

    Args:
        spline:             spline to tesselate
        arcSegmentation:    segment number
        useArcSegmentation: if use segment polygonization, set to 0
        armLength:          max length of calculated segment, for rise value polygonization only
        riseValue:          rise value

    Returns:
        tuple(bool true = success,
              result polyline)
    """
@typing.overload
def Polygonize(line: Line3D) -> tuple[bool, Polyline3D]:
    """Create polyline from line

    Args:
        line: Line to polygonize

    Returns:
        tuple(bool true = success,
              Result polyline)
    """
@typing.overload
def Polygonize(line: Line2D, fromOffset: float, toOffset: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        line:       Line which will be polygonized
        fromOffset: the offset from the elements start point, where polygonization will begin
        toOffset:   the offset from the elements start point, where polygonization will end

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(clothoid: Clothoid2D, fromOffset: float, toOffset: float, arcSegmentation: int, useArcSegmentation: int,
               armLength: float, riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        clothoid:           Clothoid which will be polygonized
        fromOffset:         the offset from the elements start point, where polygonization will begin
        toOffset:           the offset from the elements start point, where polygonization will end
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(polyline: Polyline2D, fromOffset: float, toOffset: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        polyline:   Polyline which will be polygonized
        fromOffset: the offset from the elements start point, where polygonization will begin
        toOffset:   the offset from the elements start point, where polygonization will end
        eps:        stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(polygon: Polygon2D, fromOffset: float, toOffset: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        polygon:    Polygon which will be polygonized
        fromOffset: the offset from the elements start point, where polygonization will begin
        toOffset:   the offset from the elements start point, where polygonization will end
        eps:        stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(arc: Arc2D, fromOffset: float, toOffset: float, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        arc:                Arc which will be polygonized
        fromOffset:         the offset from the elements start point, where polygonization will begin
        toOffset:           the offset from the elements start point, where polygonization will end
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(arc: Arc2D, fromOffset: float, toOffset: float, count: int, bInscribed: bool) -> tuple[bool, Polyline2D]:
    """Polygonize Arc2D with given division

    Args:
        arc:        Arc2D
        fromOffset: the offset from the elements start point, where polygonization will begin
        toOffset:   the offset from the elements start point, where polygonization will end
        count:      Count of segments
        bInscribed: in case of inscribed circle there is additional segment (one segment divided to 2 parts)

    Returns:
        tuple(bool (true = polygonization possible),
              PolyLine2D)
    """
@typing.overload
def Polygonize(spline: Spline2D, fromOffset: float, toOffset: float, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        spline:             Spline which will be polygonized
        fromOffset:         the offset from the elements start point, where polygonization will begin
        toOffset:           the offset from the elements start point, where polygonization will end
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(path: Path2D, fromOffset: float, toOffset: float, arcSegmentation: int, useArcSegmentation: int, armLength: float,
               riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonizes multiple geometry objects, if they if they follow directly one another

    emark The objects in the path must follow directly one another. This means, the start- or endpoint
            of one object has to be the start- or endpoint of the next object in the path and the other point
            of the object has to be the start- or endpoint of the previous object in the path.
            eg.: Start1-End1, End2-Start2, End3-Start3, Start4-End4 and so on.
            where, End1 == End2, Start2 == End3, Start3 == Start4

            If they don't follow one another, it's unknown how the calculated polyline will look.

            The parameters: arcSegmentation, useArcSegmentation, armLength, riseValue are not relevant for lines and polylines.
            eps is only relevant if, there is a spline or clothoid in the vector.
            See class-description for more information about these parameters.

    Args:
        path:               The vector with the objects, which will be polygonized
        fromOffset:         the offset from the elements start point, where polygonization will begin
        toOffset:           the offset from the elements start point, where polygonization will end
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
@typing.overload
def Polygonize(area: ClosedAreaComposite2D, eps: float, arcSegmentation: int = 360, useArcSegmentation: int = 0, armLength: float = 0.0,
               riseValue: float = 0.0) -> tuple[bool, Polygon2D]:
    """Polygonizes path bounded area

    Args:
        area:               path bounded area to be polygonized
        eps:                Number of segments the arc will be divided
        arcSegmentation:    type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        useArcSegmentation: maximum length of a segment for polygonized arc
        armLength:          is the maximum distance from the actual arc and the polyline
        riseValue:          stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the resulting polygon)
    """
@typing.overload
def Polygonize(geometry_object: object, fromOffset: float, toOffset: float, arcSegmentation: int, useArcSegmentation: int,
               armLength: float, riseValue: float, eps: float) -> tuple[bool, Polyline2D]:
    """Polygonize a single geometry object
    emark   The polygonization is always done in the direction of the element and therefor for non-cyclic elements
              the fromOffset must be smaller than the toOffset

    Args:
        geometry_object:    Geometry object which will be polygonized
        fromOffset:         the offset from the elements start point, where polygonization will begin
        toOffset:           the offset from the elements start point, where polygonization will end
        arcSegmentation:    Number of segments the arc will be divided
        useArcSegmentation: type of the polygonization (if 0 use the arcSegmentation otherwise use the riseValue)
        armLength:          maximum length of a segment for polygonized arc
        riseValue:          is the maximum distance from the actual arc and the polyline
        eps:                stw[295-1]

    Returns:
        tuple(true, if calculation completes, false: if something went wrong during the calculation,
              the polyline will be filled with the points of the polygonization)
    """
def Polygonize(self):
    """ Overloaded function. See individual overloads.
    """
def PolygonizeEqually(arc: Arc2D, fromPoint: Point2D, toPoint: Point2D, count: int) -> tuple[bool, Polyline2D]:
    """Polygonize given arc always equally

    Args:
        arc:       Source arc
        fromPoint: Start point for polygonization
        toPoint:   End point for polygonization
        count:     Count of segments

    Returns:
        tuple(bool (true = polygonization possible),
              Output polyline)
    """
@typing.overload
def Rotate(point: Point2D, angle: Angle) -> Point2D:
    """Rotate a point around zero point by an angle.

    Args:
        point: 2D Point
        angle: Angle

    Returns:
        Resulting 2D Point
    """
@typing.overload
def Rotate(point: Point2D, zeroPoint: Point2D, angle: Angle) -> Point2D:
    """Rotate a point around given point by an angle.

    Args:
        point:     2D Point
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D point
    """
@typing.overload
def Rotate(line: Line2D, angle: Angle) -> Line2D:
    """Rotate a line around zero point by an angle.

    Args:
        line:  2D line
        angle: Angle

    Returns:
        Resulting 2D line
    """
@typing.overload
def Rotate(line: Line2D, zeroPoint: Point2D, angle: Angle) -> Line2D:
    """Rotate a line around given point by an angle.

    Args:
        line:      2D line
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D line
    """
@typing.overload
def Rotate(arc: Arc2D, angle: Angle) -> Arc2D:
    """Rotate a arc around zero point by an angle.

    This function rotate center point and start and end angles.

    Args:
        arc:   2D arc
        angle: Angle

    Returns:
        Resulting 2D arc
    """
@typing.overload
def Rotate(arc: Arc2D, zeroPoint: Point2D, angle: Angle) -> Arc2D:
    """Rotate a arc around given point by an angle.

    This function rotate center point start and end angles.

    Args:
        arc:       2D arc
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D arc
    """
@typing.overload
def Rotate(vec: Vector2D, angle: Angle) -> Vector2D:
    """Rotate a vector by an angle.

    Args:
        vec:   2D vector
        angle: Angle

    Returns:
        Resulting 2D vector
    """
@typing.overload
def Rotate(vec: Vector3D, axis: Axis3D, angle: Angle) -> Vector3D:
    """Rotate a vector by an angle.

    Args:
        vec:   3D vector
        axis:  3D axis
        angle: Angle of rotation

    Returns:
        Resulting 3D vector
    """
@typing.overload
def Rotate(polyline: Polyline2D, zeroPoint: Point2D, angle: Angle) -> Polyline2D:
    """Rotate a polyline around given point by an angle.

    Args:
        polyline:  2D polyline
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D polyline
    """
@typing.overload
def Rotate(polyline: Polyline2D, angle: Angle) -> Polyline2D:
    """Rotate a polyline around origin by an angle.

    Args:
        polyline: 2D polyline
        angle:    Angle of rotation

    Returns:
        Resulting 2D polyline
    """
@typing.overload
def Rotate(axis: Axis2D, angle: Angle) -> Axis2D:
    """Rotate a axis around origin by an angle.

    Args:
        axis:  2D axis
        angle: Angle of rotation

    Returns:
        Resulting 2D axis
    """
@typing.overload
def Rotate(axis: Axis2D, zeroPoint: Point2D, angle: Angle) -> Axis2D:
    """Rotate a axis around given point by an angle.

    Args:
        axis:      2D axis
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D axis
    """
@typing.overload
def Rotate(axis: AxisPlacement2D, angle: Angle) -> AxisPlacement2D:
    """Rotate a axis placement around origin by an angle.

    Args:
        placement: 2D axis placement
        angle:     Angle of rotation

    Returns:
        Resulting 2D axis placement
    """
@typing.overload
def Rotate(axis: AxisPlacement2D, zeroPoint: Point2D, angle: Angle) -> AxisPlacement2D:
    """Rotate a axis placement around given point by an angle.

    Args:
        placement: 2D axis placement
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D axis placement
    """
@typing.overload
def Rotate(placement: AxisPlacement3D, angle: Angle) -> AxisPlacement3D:
    """Rotate a axis placement3D around origin(z-axis) by an angle.

    Args:
        placement: 3D axis placement
        angle:     Angle of rotation

    Returns:
        Resulting 3D axis placement
    """
@typing.overload
def Rotate(placement: AxisPlacement3D, rotAxis: Axis3D, angle: Angle) -> AxisPlacement3D:
    """Rotate a axis placement 3D around origin(z-axis) by an angle.

    Args:
        placement: 3D axis placement
        rotAxis:   3D axis
        angle:     Angle of rotation

    Returns:
        Resulting 3D Axis placement
    """
@typing.overload
def Rotate(placement: AxisPlacement3D, zeroPoint: Point2D, angle: Angle) -> AxisPlacement3D:
    """Rotate a axis placement around given point (z-axis) by an angle.

    Args:
        placement: 3D axis placement
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D axis placement
    """
@typing.overload
def Rotate(clothoid: Clothoid2D, angle: Angle) -> Clothoid2D:
    """Rotate a clothoid around origin by an angle.

    Args:
        clothoid: 2D clothoid
        angle:    Angle of rotation

    Returns:
        Resulting 2D clothoid
    """
@typing.overload
def Rotate(clothoid: Clothoid2D, zeroPoint: Point2D, angle: Angle) -> Clothoid2D:
    """Rotate a clothoid around given point by an angle.

    Args:
        clothoid:  2D clothoid
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D clothoid
    """
@typing.overload
def Rotate(polygon: Polygon2D, angle: Angle) -> Polygon2D:
    """Rotate a polygon around origin by an angle.

    Args:
        polygon: 2D polygon
        angle:   Angle of rotation

    Returns:
        Resulting 2D polygon
    """
@typing.overload
def Rotate(polygon: Polygon2D, zeroPoint: Point2D, angle: Angle) -> Polygon2D:
    """Rotate a polygon around given point by an angle.

    Args:
        polygon:   2D polygon
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D polygon
    """
@typing.overload
def Rotate(area: PolygonalArea2D, angle: Angle) -> PolygonalArea2D:
    """Rotate a polygonal area around origin by an angle.

    Args:
        area:  2D polygonal area
        angle: Angle of rotation

    Returns:
        Resulting 2D polygonal area
    """
@typing.overload
def Rotate(area: PolygonalArea2D, zeroPoint: Point2D, angle: Angle) -> PolygonalArea2D:
    """Rotate a polygonal area around given point by an angle.

    Args:
        area:      2D polygonal area
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D polygonal area
    """
@typing.overload
def Rotate(spline: Spline2D, angle: Angle) -> Spline2D:
    """Rotate a spline around origin by an angle.

    Args:
        spline:    2D spline
        angle: Angle of rotation

    Returns:
        Resulting 2D spline
    """
@typing.overload
def Rotate(spline: Spline2D, zeroPoint: Point2D, angle: Angle) -> Spline2D:
    """Rotate a spline around given point by an angle.

    Args:
        spline:    2D spline
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 2D spline
    """
@typing.overload
def Rotate(point: Point3D, angle: Angle) -> Point3D:
    """Rotate a 3D point around origin by an angle.

    Args:
        point: 3D point
        angle: Angle of rotation

    Returns:
        Resulting 3D point
    """
@typing.overload
def Rotate(point: Point3D, zeroPoint: Point2D, angle: Angle) -> Point3D:
    """Rotate a 3D point around given 2D point by an angle.

    Args:
        point:     3D point
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D point
    """
@typing.overload
def Rotate(point: Point3D, axis: Axis3D, angle: Angle) -> Point3D:
    """Rotate a 3D point around given 3D axis by an angle.

    Args:
        point: 3D point
        axis:  3D axis
        angle: Angle of rotation

    Returns:
        Resulting 3D point
    """
@typing.overload
def Rotate(line: Line3D, zeroPoint: Point2D, angle: Angle) -> Line3D:
    """Rotate a 3D line around given 2D point by an angle.

    Args:
        line:      3D line
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D line
    """
@typing.overload
def Rotate(cylinder: Cylinder3D, angle: Angle) -> Cylinder3D:
    """Rotate a 3D Cylinder around origin by an angle.

    Args:
        cylinder: 3D Cylinder
        angle: Angle of rotation

    Returns:
        Resulting 3D Cylinder
    """
@typing.overload
def Rotate(cylinder: Cylinder3D, zeroPoint: Point2D, angle: Angle) -> Cylinder3D:
    """Rotate a 3D Cylinder around  given 2D point by an angle.

    Args:
        cylinder: 3D Cylinder
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D Cylinder
    """
@typing.overload
def Rotate(cylinder: Cylinder3D, axis: Axis3D, angle: Angle) -> Cylinder3D:
    """Rotate a 3D Cylinder around given 3D axis by an angle.

    Args:
        cylinder: 3D Cylinder
        axis:     3D axis
        angle:    Angle of rotation

    Returns:
        Resulting 3D Cylinder
    """
@typing.overload
def Rotate(ellipsoid: Ellipsoid3D, angle: Angle) -> Ellipsoid3D:
    """Args:
        ellipsoid: 3D Ellipsoid
        angle: Angle of rotation

    Returns:
        Resulting 3D Ellipsoid
    """
@typing.overload
def Rotate(ellipsoid: Ellipsoid3D, zeroPoint: Point2D, angle: Angle) -> Ellipsoid3D:
    """Rotate a 3D Ellipsoid around given 2D point by an angle.

    Args:
        ellipsoid: 3D Ellipsoid
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D Ellipsoid
    """
@typing.overload
def Rotate(ellipsoid: Ellipsoid3D, axis: Axis3D, angle: Angle) -> Ellipsoid3D:
    """Rotate a 3D Ellipsoid around given 3D axis by an angle.

    Args:
        ellipsoid: 3D Ellipsoid
        axis:      3D axis
        angle:     Angle of rotation

    Returns:
        Resulting 3D Ellipsoid
    """
@typing.overload
def Rotate(cone: Cone3D, angle: Angle) -> Cone3D:
    """Rotate a 3D Cone around origin by an angle.

    Args:
        cone:  3D Cone
        angle: Angle of rotation

    Returns:
        Resulting 3D Cone
    """
@typing.overload
def Rotate(cone: Cone3D, zeroPoint: Point2D, angle: Angle) -> Cone3D:
    """Rotate a 3D Cone around  given 2D point by an angle.

    Args:
        cone:      3D Cone
        zeroPoint: 2D zero point
        angle:     Angle of rotation

    Returns:
        Resulting 3D Cone
    """
@typing.overload
def Rotate(cone: Cone3D, axis: Axis3D, angle: Angle) -> Cone3D:
    """Rotate a 3D Cone around given 3D axis by an angle.

    Args:
        cone:  3D Cone
        axis:  3D axis
        angle: Angle of rotation

    Returns:
        Resulting 3D Cone
    """
@typing.overload
def Rotate(minmax: MinMax2D, angle: Angle) -> MinMax2D:
    """Rotate a MinMax2D by an angle.

    Args:
        minmax: 2D MinMax
        angle:  Angle of rotation

    Returns:
        Resulting 2D MinMax
    """
@typing.overload
def Rotate(brep: BRep3D, axis: Axis3D, angle: Angle) -> BRep3D:
    """Rotate a brep around given 3D axis by an angle.

    Args:
        brep:  brep
        axis:  3D axis
        angle: Angle of rotation

    Returns:
        brep
    """
@typing.overload
def Rotate(polyhedron: Polyhedron3D, axis: Axis3D, angle: Angle) -> Polyhedron3D:
    """Rotate a polyhedron around given 3D axis by an angle.

    Args:
        polyhedron:polyhedron
        axis:  3D axis
        angle: Angle of rotation

    Returns:
        polyhedron
    """
def Rotate(self):
    """ Overloaded function. See individual overloads.
    """
def SetAbsoluteTolerance(value: float):
    """set absolute tolerance

    Args:
        value: new value
    """
def SetAngleTolerance(value: Angle):
    """Set angle tolerance

    This tolerance is using for angle comparison.

    Args:
        value: New tolerance using for angle comparison [rad]
    """
def SetCurvatureTolerance(value: float):
    """Set curvature tolerance

    This tolerance is using for curvature comparison.

    Args:
        value: New tolerance using for curvature comparison
    """
def SetCurveLengthTolerance(value: float):
    """Set curve length tolerance

    This tolerance is using for length of curve comparison.

    Args:
        value: New tolerance using for length of curve comparison [mm]
    """
def SetRelativeTolerance(value: float):
    """set relative tolerance

    Args:
        value: new value
    """
def SetZValue(zValue: float, line: Line3D):
    """Set the the z value of a line

    Args:
        zValue: zValue
        line:   line

    Returns:
        true, if the calculation was correct
    """
@typing.overload
def Split(polygon2D: Polygon2D, splitPoints: Point3DList, pSplitGeometry: object, posTol: float) -> tuple[eSplitResult,
          list[Polygon2D]]:
    """Split a Polygon2D into multiple Polygon2D geometries by given split points

    Args:
        polygon2D:      The polygon to split
        splitPoints:    The given split points (e.g. intersection points between polygon2D and splitGeometry)
        pSplitGeometry: Can be NULL. The Geometry who splits the element. If available it maybe used as alternative for splitPoints
        posTol:         Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split polygons. Usually this vector has cardinality of two.
                                          First polygon is BoolOp of 'given polygon - splitPolygon'. Second polygon is BoolOp of 'given polygon& splitPolygon'.
                                          The splitPolygon is created from splitPoints)
    """
@typing.overload
def Split(line2D: Line2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Line2D]]:
    """Split a Line2D into multiple Line2D geometries by given split points

    Args:
        line2D:      The line to split
        splitPoints: The given split points (e.g. intersection points onto the line)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split lines)
    """
@typing.overload
def Split(polyline2D: Polyline2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Polyline2D]]:
    """Split a Polyline2D into multiple Polyline2D geometries by given split points

    Args:
        polyline2D:  The polyline to split
        splitPoints: The given split points (e.g. intersection points onto the polyline)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split polylines)
    """
@typing.overload
def Split(spline2D: Spline2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Spline2D]]:
    """Split a Spline2D into multiple Spline2D geometries by given split points

    Args:
        spline2D:    The spline to split
        splitPoints: The given split points (e.g. intersection points onto the spline)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split splines)
    """
@typing.overload
def Split(spline3D: Spline3D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Spline3D]]:
    """Split a Spline3D into multiple Spline3D geometries by given split points

    Args:
        spline3D:    The spline to split
        splitPoints: The given split points (e.g. intersection points onto the spline)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split splines)
    """
@typing.overload
def Split(polyline2D: Polyline2D, polygon2D: Polygon2D, posTol: float) -> tuple[eSplitResult, list[Polyline2D], list[Polyline2D]]:
    """Split a Polyline2D into multiple Polyline2D geometries by given split polygon

    Args:
        polyline2D: The polyline to split
        polygon2D:  The given polygon
        posTol:     Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split polylines inside polygon,
              Vector of split polylines outside polygon)
    """
@typing.overload
def Split(polygon: Polygon2D, polyline: Polyline2D, posTol: float, divideComponents: bool) -> tuple[eSplitResult, Polygon2D, Polygon2D,
          Polygon2D]:
    """Split Polygon2D into 3 polygons by given Polyline2D

    Args:
        polygon:          The polygon to split
        polyline:         The given polyline
        posTol:           Tolerance being used to determine the position of split points on the input curve
        divideComponents: If true, polygon will be split by intersection points of polyline and connection lines between components

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Polygon, which consist of not split components,
              Polygon, which consist of components on left side of polyline,
              Polygon, which consist of components on right side of polyline)
    """
@typing.overload
def Split(polygon: Polygon2D, axis: Axis2D, posTol: float, divideComponents: bool) -> tuple[eSplitResult, Polygon2D, Polygon2D,
          Polygon2D]:
    """Split Polygon2D into 3 polygons by given Axis2D

    Args:
        polygon:          The polygon to split
        axis:             The given axis
        posTol:           Tolerance being used to determine the position of split points on the input curve
        divideComponents: If true, polygon will be split by intersection points of polyline and connection lines between components

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Polygon, which consist of not split components,
              Polygon, which consist of components on left side of polyline,
              Polygon, which consist of components on right side of polyline)
    """
@typing.overload
def Split(line3D: Line3D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Line3D]]:
    """Split a Line3D into multiple Line3D geometries by given split points

    Args:
        line3D:      The line to split
        splitPoints: The given split points (e.g. intersection points onto the line)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split lines)
    """
@typing.overload
def Split(polyline3D: Polyline3D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Polyline3D]]:
    """Split a Polyline3D into multiple Polyline3D geometries by given split points

    Args:
        polyline3D:  The polyline to split
        splitPoints: The given split points (e.g. intersection points onto the line)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split polylines)
    """
@typing.overload
def Split(arc3D: Arc3D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Arc3D]]:
    """Split a Arc3D into multiple Arc3D geometries by given split points

    Args:
        arc3D:       The arc to split
        splitPoints: The given split points (e.g. intersection points onto the line)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split arcs)
    """
@typing.overload
def Split(arc2D: Arc2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Arc2D]]:
    """Split a Arc2D into multiple Arc2D geometries by given split points

    Args:
        arc2D:       The arc to split
        splitPoints: The given split points (e.g. intersection points onto the arc)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split arcs)
    """
@typing.overload
def Split(clothoid2D: Clothoid2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[Clothoid2D]]:
    """Split a Clothoid2D into multiple Clothoid2D geometries by given split points

    Args:
        clothoid2D:  The clothoid to split
        splitPoints: The given split points (e.g. intersection points onto the clothoid)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split clothoids)
    """
@typing.overload
def Split(bspline2D: BSpline2D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[BSpline2D]]:
    """Split a BSpline2D  into multiple BSpline2D geometries by given split points

    Args:
        bspline2D:   The spline to split
        splitPoints: The given split points (e.g. intersection points onto the spline)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split splines)
    """
@typing.overload
def Split(bspline3D: BSpline3D, splitPoints: Point3DList, posTol: float) -> tuple[eSplitResult, list[BSpline3D]]:
    """Split a BSpline3D  into multiple BSpline3D geometries by given split points

    Args:
        bspline3D:   The spline to split
        splitPoints: The given split points (e.g. intersection points onto the spline)
        posTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Vector of split splines)
    """
@typing.overload
def Split(baseGeometry: object, point: Point3D, bGetFirstHalf: bool, eps: float) -> object:
    """Split the element in two and return one half

    Args:
        baseGeometry:  Geometry will be split
        point:         Split point
        bGetFirstHalf: True, if the given point should be
        eps:           Tolerance

    Returns:
        first or second half or nullptr
    """
def Split(self):
    """ Overloaded function. See individual overloads.
    """
def SplitPolygon3DToParts(polygon: Polygon3D) -> tuple:
    """Splits normalized Polygon3D into parts

    Args:
        polygon: Normalized 3D polygon

    Returns:
         eOK if converted successful, else eError,
        Vector of parts (loops)
    """
@typing.overload
def Tesselate(brep: BRep3D, density: float, maxAngle: float, minEdge: float, maxEdge: float) -> tuple:
    """Tesselate b-rep with mesh triangles

    Args:
        brep:     brep to be tesselated
        density:  density of resulting mesh (when 0, not used)
        maxAngle: maximal angle between neighbor triangles in degrees (when 0, not used)
        minEdge:  minimal edge length (when 0, not used)
        maxEdge:  maximal edge length (when 0, not used)

    Returns:
         error code,
         resulting tesselated polyhedron
    """
@typing.overload
def Tesselate(brep: BRep3D, density: float, chord: float, maxAngle: float, minEdge: float, maxEdge: float) -> tuple:
    """Tesselate b-rep with mesh triangles

    Args:
        brep:     brep to be tesselated
        density:  density of resulting mesh (when 0, not used)
        chord:    curve/surface chord tolerance (when 0, not used)
        maxAngle: maximal angle between neighbor triangles in degrees (when 0, not used)
        minEdge:  minimal edge length (when 0, not used)
        maxEdge:  maximal edge length (when 0, not used)

    Returns:
         error code,
         resulting tesselated polyhedron
    """
def Tesselate(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def Touching(line1: Line2D, line2: Line2D) -> bool:
    """Test for collision between 2 line2D objects

    Args:
        line1: the first geometry object
        line2: the second geometry object

    Returns:
        true when in touch, otherwise false.
    """
@typing.overload
def Touching(polygon1: Polygon2D, polygon2: Polygon2D) -> bool:
    """Test for collision between 2 polygon2D objects

    Args:
        polygon1: the first geometry object
        polygon2: the second geometry object

    Returns:
        true when 1 or more lines in touch, otherwise false.
    """
@typing.overload
def Touching(polygon: Polygon2D, polyline: Polyline2D) -> bool:
    """Test for collision between polygon2D and polyline2D

    Args:
        polygon:  the first geometry object
        polyline: the second geometry object

    Returns:
        true when 1 or more lines in touch, otherwise false.
    """
def Touching(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def Transform(point: Point2D, matrix: Matrix2D) -> Point2D:
    """Point2D matrix transformation.

    Args:
        point:  2D point to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(line: Line2D, matrix: Matrix2D) -> Line2D:
    """Line2D matrix transformation.

    Args:
        line:   2D line to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(vec: Vector2D, matrix: Matrix2D) -> Vector2D:
    """Vector2D matrix transformation.

    Args:
        vec:    2D vector to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(arc: Arc2D, matrix: Matrix2D) -> Arc2D:
    """Arc2D matrix transformation.

    Args:
        arc:    2D arc to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(clothoid: Clothoid2D, matrix: Matrix2D) -> Clothoid2D:
    """Clothoid2D matrix transformation.

    Args:
        clothoid: 2D clothoid to transform.
        matrix:   Transformation Matrix.
    """
@typing.overload
def Transform(spline: Spline2D, matrix: Matrix2D) -> Spline2D:
    """Spline2D matrix transformation.

    Args:
        spline: 2D spline to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(axis: Axis2D, matrix: Matrix2D) -> Axis2D:
    """Axis2D matrix transformation.

    Args:
        axis:   2D axis to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(polyline: Polyline2D, matrix: Matrix2D) -> Polyline2D:
    """Polyline2D matrix transformation.

    Args:
        polyline: 2D polyline to transform.
        matrix:   Transformation Matrix.
    """
@typing.overload
def Transform(path: Path2D, matrix: Matrix2D) -> Path2D:
    """Path2D matrix transformation.

    Args:
        path:   2D path to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(area: PolygonalArea2D, matrix: Matrix2D) -> PolygonalArea2D:
    """PolygonalArea2D matrix transformation.

    Args:
        area:   2D polygonal area which will be transformed
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(area: ClosedArea2D, matrix: Matrix2D) -> ClosedArea2D:
    """ClosedArea2D matrix transformation.

    Args:
        area:   2D path bounded area which will be transformed
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(area: ClosedAreaComposite2D, matrix: Matrix2D) -> ClosedAreaComposite2D:
    """ClosedAreaComposite2D matrix transformation.

    Args:
        area:   2D path bounded area composite which will be transformed
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(point: Point3D, matrix: Matrix3D) -> Point3D:
    """Point3D matrix3D transformation.

    Args:
        point:  3D point to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(point: Point3D, matrix: Matrix2D) -> Point3D:
    """Point3D matrix2D transformation.

    Args:
        point:  3D point to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(el: Line3D, matrix: Matrix3D) -> Line3D:
    """Line3D matrix3D transformation.

    Args:
        el:     3D line to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(el: Line3D, matrix: Matrix2D) -> Line3D:
    """Line3D matrix2D transformation.

    Args:
        el:     3D line to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(vec: Vector3D, matrix: Matrix3D) -> Vector3D:
    """Vector3D matrix3D transformation.

    Args:
        vec:    3D vector to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(vec: Vector3D, matrix: Matrix2D) -> Vector3D:
    """Vector3D matrix2D transformation.

    Args:
        vec:    3D vector to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(arc: Arc3D, matrix: Matrix3D) -> Arc3D:
    """Arc3D matrix3D transformation.

    Args:
        arc:    3D arc to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(arc: Arc3D, matrix: Matrix2D) -> Arc3D:
    """Arc3D matrix2D transformation.

    Args:
        arc:    3D arc to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(cuboid: Cuboid3D, matrix: Matrix3D) -> Cuboid3D:
    """Cuboid3D matrix3D transformation.

    Args:
        cuboid: 3D cuboid to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(cuboid: Cuboid3D, matrix: Matrix2D) -> Cuboid3D:
    """Cuboid3D matrix2D transformation.

    Args:
        cuboid: 3D cuboid to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(plane: Plane3D, matrix: Matrix3D) -> Plane3D:
    """Plane3D matrix3D transformation.

    Args:
        plane:  3D plane to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(plane: Plane3D, matrix: Matrix2D) -> Plane3D:
    """Plane3D matrix2D transformation.

    Args:
        plane:  2D plane to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(polygon: Polygon2D, matrix: Matrix2D) -> Polygon2D:
    """Polyline2D matrix transformation.

    Args:
        polygon: 2D polygon to transform.
        matrix:  Transformation Matrix.
    """
@typing.overload
def Transform(polygon: Polygon3D, matrix: Matrix2D) -> Polygon3D:
    """Polygon3D matrix transformation.

    Args:
        polygon: 3D polygon to transform.
        matrix:  Transformation Matrix.
    """
@typing.overload
def Transform(polygon: Polygon3D, matrix: Matrix3D) -> Polygon3D:
    """Polygon3D matrix transformation.

    Args:
        polygon: 3D polygon to transform.
        matrix:  Transformation Matrix.
    """
@typing.overload
def Transform(polyline: Polyline3D, matrix: Matrix2D) -> Polyline3D:
    """Polyline3D matrix transformation.

    Args:
        polyline: 3D polyline to transform.
        matrix:   Transformation Matrix.
    """
@typing.overload
def Transform(polyline: Polyline3D, matrix: Matrix3D) -> Polyline3D:
    """Polyline3D matrix transformation.

    Args:
        polyline: 3D polyline to transform.
        matrix:   Transformation Matrix.
    """
@typing.overload
def Transform(spline: Spline3D, matrix: Matrix3D) -> Spline3D:
    """Spline3D matrix transformation.

    Args:
        spline: 3D spline to transform.
        matrix: Transformation Matrix.
    """
@typing.overload
def Transform(polyhedron: Polyhedron3D, matrix: Matrix3D) -> Polyhedron3D:
    """Polyhedron3D matrix3D transformation.

    Args:
        polyhedron: 3D polyhedron to transform.
        matrix:     Transformation 3D Matrix.
    """
@typing.overload
def Transform(polyhedron: Polyhedron3D, matrix: Matrix2D) -> Polyhedron3D:
    """Polyhedron3D matrix2D transformation.

    Args:
        polyhedron: 3D polyhedron to transform.
        matrix:     Transformation 2D Matrix.
    """
@typing.overload
def Transform(axis: Axis3D, matrix: Matrix2D) -> Axis3D:
    """Axis3D matrix2D transformation.

    Args:
        axis:   3D axis to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(axis: Axis3D, matrix: Matrix3D) -> Axis3D:
    """Axis3D matrix3D transformation.

    Args:
        axis:   3D axis to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(path: Path3D, matrix: Matrix3D) -> Path3D:
    """Path3D matrix3D transformation.

    Args:
        path:   3D path to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(path: Path3D, matrix: Matrix2D) -> Path3D:
    """Path3D matrix2D transformation.

    Args:
        path:   3D path to transform.
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(area: PolygonalArea3D, matrix: Matrix2D) -> PolygonalArea3D:
    """PolygonalArea3D matrix2D transformation.

    Args:
        area:   3D polygonal area which will be transformed
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(area: PolygonalArea3D, matrix: Matrix3D) -> PolygonalArea3D:
    """PolygonalArea3D matrix3D transformation.

    Args:
        area:   3D polygonal area which will be transformed
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(solid: ClippedSweptSolid3D, matrix: Matrix2D) -> ClippedSweptSolid3D:
    """ClippedSweptSolid3D matrix2D transformation.

    Args:
        solid:  ClippedSweptSolid3D which will be transformed
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(solid: ClippedSweptSolid3D, matrix: Matrix3D) -> ClippedSweptSolid3D:
    """ClippedSweptSolid3D matrix3D transformation.

    This body is transformed by 2D transformations only to keep vertical extrusion of the profile.

    Args:
        solid:  ClippedSweptSolid3D which will be transformed
        matrix: Transformation 2D Matrix.
    """
@typing.overload
def Transform(cylinder: Cylinder3D, matrix: Matrix2D) -> Cylinder3D:
    """Cylinder3D matrix2D transformation.

    Args:
        cylinder: Cylinder3D which will be transformed
        matrix:   Transformation 2D Matrix.

    Warning: Perspective transformation will not work correctly
    """
@typing.overload
def Transform(cylinder: Cylinder3D, matrix: Matrix3D) -> Cylinder3D:
    """Cylinder3D matrix3D transformation.

    Args:
        cylinder: Cylinder3D which will be transformed
        matrix:   Transformation 3D Matrix.

    Warning: Perspective transformation will not work correctly
    """
@typing.overload
def Transform(ellipsoid: Ellipsoid3D, matrix: Matrix2D) -> Ellipsoid3D:
    """Ellipsoid3D matrix2D transformation.

    Args:
        ellipsoid: Ellipsoid3D which will be transformed
        matrix:    Transformation 2D Matrix.

    Warning: Perspective transformation will not work correctly
    """
@typing.overload
def Transform(ellipsoid: Ellipsoid3D, matrix: Matrix3D) -> Ellipsoid3D:
    """Ellipsoid3D matrix3D transformation.

    Args:
        ellipsoid: Ellipsoid3D which will be transformed
        matrix:    Transformation 3D Matrix.

    Warning: Perspective transformation will not work correctly
    """
@typing.overload
def Transform(brep: BRep3D, matrix: Matrix3D) -> BRep3D:
    """BRep3D matrix3D transformation.

    Args:
        brep:   Brep3D to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(brep: BRep3D, matrix: Matrix2D) -> BRep3D:
    """BRep3D matrix2D transformation.

    Args:
        brep:   Brep3D to transform.
        matrix: Transformation 3D Matrix.
    """
@typing.overload
def Transform(spline: BSpline3D, matrix: Matrix3D) -> BSpline3D:
    """BSpline3D matrix transformation

    Args:
        spline: Bspline3D to transform
        matrix: Transformation 3D matrix
    """
@typing.overload
def Transform(spline: BSpline3D, matrix: Matrix2D) -> BSpline3D:
    """BSpline3D matrix transformation

    Args:
        spline: Bspline3D to transform
        matrix: Transformation 2D matrix
    """
@typing.overload
def Transform(cone: Cone3D, matrix: Matrix3D) -> Cone3D:
    """Cone3D matrix transformation

    Args:
        cone:   Cone3D to transform
        matrix: Transformation 3D matrix
    """
@typing.overload
def Transform(cone: Cone3D, matrix: Matrix2D) -> Cone3D:
    """Cone3D matrix transformation

    Args:
        cone:   Cone3D to transform
        matrix: Transformation 2D matrix
    """
def Transform(self):
    """ Overloaded function. See individual overloads.
    """
@typing.overload
def Trim(spline: Spline2D, useStartSpline: bool, point1: Point2D, useEndSpline: bool, point2: Point2D,
         splineTol: float) -> tuple[eSplitResult, Spline2D]:
    """Trim a Spline2D by given trim points

    Flags useStartSpline, useEndSpline are optional and can not be never used,
    but if these flags are used, then calculation is faster.
    point1 and point2 are ordered during trimming when flags for spline points are not using.
    If spline flags is used, then point1 is always start point and pont2 is always end point of trimming.
    In this case, Trim function return SPLIT_INVALID_ARGS when points are in reversed order.

    Args:
        spline:         The spline to split
        useStartSpline: True when trimming is from beginning of spline, point1 is ignored
        point1:         The given trimming point1 (e.g. intersection points onto the spline)
        useEndSpline:   True when trimming is to end of spline, point2 is ignored
        point2:         The given trimming point2 (e.g. intersection points onto the spline)
        splineTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Trimmed spline)
    """
@typing.overload
def Trim(clothoid: Clothoid2D, useStartClothoid: bool, point1: Point2D, useEndClothoid: bool, point2: Point2D,
         clothoidTol: float) -> tuple[eSplitResult, Clothoid2D]:
    """Trim a Clothoid2D by given trim points

    Flags useStartClothoid, useEndClothoid are optional and can not be never used,
    but if these flags are used, then calculation is faster.
    point1 and point2 are ordered during trimming when flags for clothoid points are not using.
    If clothoid flags is used, then point1 is always start point and pont2 is always end point of trimming.
    In this case, Trim function return SPLIT_INVALID_ARGS when points are in reversed order.

    Args:
        clothoid:         The clothoid to split
        useStartClothoid: True when trimming is from beginning of clothoid, point1 is ignored
        point1:           The given trimming point1 (e.g. intersection points onto the clothoid)
        useEndClothoid:   True when trimming is to end of clothoid, point2 is ignored
        point2:           The given trimming point2 (e.g. intersection points onto the clothoid)
        clothoidTol:      Tolerance being used to determine the position of split points on the input curve

    Returns:
        tuple(eSplitResult, SPLIT_OK on success,
              Trimmed clothoid)
    """
def Trim(self):
    """ Overloaded function. See individual overloads.
    """
