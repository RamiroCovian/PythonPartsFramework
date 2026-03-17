""" implementation of the mock class for class PreviewSymbolBuilder. """

# pylint: disable=no-self-use
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name

import typing

import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW


class PreviewSymbolBuilderMock():
    """ implementation of the mock class for class PreviewSymbolBuilder
    """

    @staticmethod
    @typing.overload
    def ArrowSymbol(pnt          : AllplanGeo.Point3D,          # type: ignore
                    bDrawIso     : bool,
                    viewProj     : AllplanIFW.ViewWorldProjection,
                    colorVariant : AllplanBasisEle.ARGB,
                    widthVariant : int,
                    rotationAngle: float,
                    allWindows   : bool = True):
        """ Create an arrow symbol

        Args:
            pnt:           input point in Allplan view coordinates
            bDrawIso:      Draw the arrow symbol inside the isometric view: true/false
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            widthVariant:  Width of the symbol
            rotationAngle: Rotation angle of the rectangle
            allWindows:    Show symbol in all windows
        """

    @staticmethod
    def ArrowSymbol(pnt          : AllplanGeo.Point3D,                # type: ignore
                    bDrawIso     : bool,
                    viewProj     : AllplanIFW.ViewWorldProjection,
                    colorVariant : AllplanBasisEle.ARGB,
                    rotationAngle: float,
                    allWindows   : bool = True):
        """ Create a small arrow symbol

        Args:
            pnt:           input point in Allplan view coordinates
            bDrawIso:      Draw the arrow symbol inside the isometric view: true/false
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            rotationAngle: Rotation angle of the rectangle
            allWindows:    Show symbol in all windows
        """

    @staticmethod
    def Circle3DSymbol(refPnt: AllplanGeo.Point3D, circle: AllplanGeo.Arc3D, viewProj: AllplanIFW.ViewWorldProjection,
                       colorVariant: AllplanBasisEle.ARGB, linePattern: int, lineWidth: float):
        """Create a 3D circle symbol preview

        Args:
            refPnt:        Reference point
            circle:        3D circle
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            linePattern:   Line pattern
            lineWidth:     Width of the line
        """

    @staticmethod
    def CircleSymbol(pnt: AllplanGeo.Point3D, bDrawIso: bool, viewProj: AllplanIFW.ViewWorldProjection,
                     colorVariant: AllplanBasisEle.ARGB, radius: int):
        """Create a circle symbol

        Args:
            pnt:           Center point
            bDrawIso:      Draw the circle symbol inside the isometric view: true/false
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            radius:        Radius of the circle in pixel
        """

    @staticmethod
    @typing.overload
    def CoordCrossSymbol(plane    : AllplanGeo.Plane3D,     # type: ignore
                         armLength: int,
                         viewProj : AllplanIFW.ViewWorldProjection):
        """ Draw the coordinate cross symbol

        Args:
            plane:     Plane
            armLength: Length of the symbol arms
            viewProj:  View world projection
        """

    @staticmethod
    def CoordCrossSymbol(axisPlacement: AllplanGeo.AxisPlacement3D,               # type: ignore
                         armLength    : int,
                         viewProj     : AllplanIFW.ViewWorldProjection):
        """ Draw the coordinate cross symbol

        Args:
            axisPlacement: Axis placement
            armLength:     Length of the symbol arms
            viewProj:      View world projection
        """

    @staticmethod
    def CrossSymbol(pnt         : AllplanGeo.Point3D,
                    bDrawIso    : bool,
                    viewProj    : AllplanIFW.ViewWorldProjection,
                    colorVariant: AllplanBasisEle.ARGB,
                    widthVariant: int):
        """ Create a cross symbol

        Args:
            pnt:          input point in Allplan view coordinates
            bDrawIso:     Draw the cross symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
        """

    @staticmethod
    def FilledRectangleSymbol(pnt          : AllplanGeo.Point3D,
                              bDrawIso     : bool,
                              viewProj     : AllplanIFW.ViewWorldProjection,
                              colorVariant : AllplanBasisEle.ARGB,
                              widthVariant : int,
                              rotationAngle: float):
        """ Create a filled rectangle symbol

        Args:
            pnt:           input point in Allplan view coordinates
            bDrawIso:      Draw the rectangle symbol inside the isometric view: true/false
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            widthVariant:  Width of the symbol
            rotationAngle: Rotation angle of the rectangle
        """

    @staticmethod
    def Line3DSymbol(refPnt      : AllplanGeo.Point3D,
                     line        : AllplanGeo.Line3D,
                     viewProj    : AllplanIFW.ViewWorldProjection,
                     colorVariant: AllplanBasisEle.ARGB,
                     linePattern : int,
                     lineWidth   : int):
        """ Create a 3D line symbol preview

        Args:
            refPnt:       Reference point
            line:         3D line
            viewProj:     View world projection data
            colorVariant: Color of the preview
            linePattern:  Line pattern
            lineWidth:    Line width
        """

    @staticmethod
    def MarkSymbol(pnt         : AllplanGeo.Point3D,
                   bDrawIso    : bool,
                   viewProj    : AllplanIFW.ViewWorldProjection,
                   colorVariant: AllplanBasisEle.ARGB,
                   widthVariant: int):
        """ Create a mark symbol (drawn an x)

        Args:
            pnt:          input point in Allplan view coordinates
            bDrawIso:     Draw the mark symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
        """

    @staticmethod
    def OffsetPointSymbols(refPnt      : AllplanGeo.Point3D,
                           offPnt      : AllplanGeo.Point3D,
                           bDrawIso    : bool,
                           viewProj    : AllplanIFW.ViewWorldProjection,
                           colorVariant: AllplanBasisEle.ARGB,
                           widthVariant: int,
                           refPntAngle : float,
                           offPntAngle : float):
        """ Create the symbols for an offset point

        Args:
            refPnt:       Reference point
            offPnt:       Offset point
            bDrawIso:     Draw the arrow symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
            refPntAngle:  Angle at the reference point
            offPntAngle:  Angle at the offset point
        """

    @staticmethod
    def OrthogonalSymbol(pnt         : AllplanGeo.Point3D,
                         bDrawIso    : bool,
                         viewProj    : AllplanIFW.ViewWorldProjection,
                         colorVariant: AllplanBasisEle.ARGB,
                         widthVariant: int):
        """ Create an orthogonal symbol

        Args:
            pnt:          input point in Allplan view coordinates
            bDrawIso:     Draw the circle symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
        """

    @staticmethod
    def ParallelSymbol(pnt         : AllplanGeo.Point3D,
                       bDrawIso    : bool,
                       viewProj    : AllplanIFW.ViewWorldProjection,
                       colorVariant: AllplanBasisEle.ARGB,
                       widthVariant: int):
        """ Create a parallel symbol

        Args:
            pnt:          input point in Allplan view coordinates
            bDrawIso:     Draw the circle symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
        """
    @staticmethod
    def Polyline2DSymbol(refPnt      : AllplanGeo.Point3D,
                         polyline    : AllplanGeo.Polyline2D,
                         viewProj    : AllplanIFW.ViewWorldProjection,
                         colorVariant: AllplanBasisEle.ARGB,
                         linePattern : int):
        """ Create a 2D polyline symbol preview

        Args:
            refPnt:       Reference point
            polyline:     Polyline
            viewProj:     View world projection
            colorVariant: Color of the preview
            linePattern:  Line pattern
        """

    @staticmethod
    @typing.overload
    def Polyline3DSymbol(polyline    : AllplanGeo.Polyline3D,           # type: ignore
                         viewProj    : AllplanIFW.ViewWorldProjection,
                         colorVariant: AllplanBasisEle.ARGB,
                         linePattern : int):
        """ Create a 3D polyline symbol preview

        Args:
            polyline:     3D Polyline
            viewProj:     View world projection data
            colorVariant: Color of the preview
            linePattern:  Line pattern
        """

    @staticmethod
    def Polyline3DSymbol(refPnt      : AllplanGeo.Point3D,                    # type: ignore
                         polyline    : AllplanGeo.Polyline3D,
                         viewProj    : AllplanIFW.ViewWorldProjection,
                         colorVariant: AllplanBasisEle.ARGB,
                         linePattern : int):
        """ Create a 3D polyline symbol preview

        Args:
            refPnt:       Reference point
            polyline:     Polyline
            viewProj:     View world projection
            colorVariant: Color of the preview
            linePattern:  Line pattern
        """

    @staticmethod
    def TrackLine(line         : AllplanGeo.Line3D,
                  bDrawIso     : bool,
                  viewProj     : AllplanIFW.ViewWorldProjection,
                  colorVariant : AllplanBasisEle.ARGB,
                  trackLineType: object):
        """ Create a track line

        Args:
            line:          Track line
            bDrawIso:      Draw the circle symbol inside the isometric view: true/false
            viewProj:      View world projection data
            colorVariant:  Color of the preview
            trackLineType: Type of the track line
        """

    @staticmethod
    def TrackMarkSymbol(pnt         : AllplanGeo.Point3D,
                        bDrawIso    : bool,
                        viewProj    : AllplanIFW.ViewWorldProjection,
                        colorVariant: AllplanBasisEle.ARGB,
                        widthVariant: int):
        """ Create a track mark symbol

        Args:
            pnt:          input point in Allplan view coordinates
            bDrawIso:     Draw the circle symbol inside the isometric view: true/false
            viewProj:     View world projection data
            colorVariant: Color of the preview
            widthVariant: Width of the symbol
        """
    @staticmethod
    def LocalCoordinateSystem(coordSystemMatrix: AllplanGeo.Matrix3D, flags: AllplanIFW.LCS_Flags, maxSize: float):
        """Create a symbol for a local coordinate system

        Args:
            coordSystemMatrix:  Matrix of the coordinate system
            flags:              Coordinate system flags
            maxSize:            Max size of the coordinate system
        """
