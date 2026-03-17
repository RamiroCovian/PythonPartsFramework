""" implementation of the CoordinateInput mock. """

#pylint: disable=missing-function-docstring
#pylint: disable=invalid-name
#pylint: disable=no-self-use
#pylint: disable=no-member

from typing import Any

from collections.abc import Callable

import math

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

from DocumentManager import DocumentManager

from TypeCollections import GeometryTyping

def trackcalls(func: Callable) -> Callable:
    """ decorator for the function call tracking

    Args:
        func: function to track

    Returns:
        function wrapper
    """

    def wrapper(*args: Any) -> Any:
        """ function wrapper

        Args:
            *args: arguments

        Returns:
            function result
        """
        if args[1] is not None:
            wrapper.has_been_called = True
        else:
            wrapper.has_been_called = False
        return func(*args)

    wrapper.has_been_called = False

    return wrapper


class CoordinateInputResult():
    """ implementation of the CoordinateInputResult mock """

    def __init__(self,
                 pnt     : AllplanGeo.Point3D,
                 pnt_type: Any):
        """ initialize

        Args:
            pnt:      input point in Allplan view coordinates
            pnt_type: point type
        """
        self.pnt      = pnt
        self.pnt_type = pnt_type


    def GetPoint(self) -> AllplanGeo.Point3D:
        """ get the point

        Returns:
            point
        """
        return self.pnt


class CoordinateInputMock():
    """ implementation of the CoordinateInput mock """

    def __init__(self,
                 doc: (AllplanEleAdapter.DocumentAdapter | None) = None):
        """ initialize

        Args:
            doc: document of the Allplan drawing files
        """

        self.input_point      = AllplanGeo.Point3D()
        self.geo_ele          = None
        self.is_valid_doc     = doc is not None
        self.doc              = doc if doc is not None else DocumentManager.get_instance().document
        self.abscissa_ele     = None
        self.selected_element = AllplanEleAdapter.BaseElementAdapter()
        self.input_plane      = None
        self.input_value      = 0


    #--------------------- helper function for setting the input results

    def SetInputPoint(self,
                      input_point: AllplanGeo.Point3D):
        """ set the input point

        Args:
            input_point: input point
        """

        self.input_point = input_point


    def SetSelectedGeometryElement(self,
                                   geo_ele: AllplanEleAdapter.BaseElementAdapter):
        """ set the selected geometry element

        Args:
            geo_ele: geometry element
        """

        self.geo_ele = geo_ele


    def SetSelectedElement(self,
                           sel_ele: AllplanEleAdapter.BaseElementAdapter):
        """ set the selected element

        Args:
            sel_ele: selected element
        """
        self.selected_element = sel_ele

    @trackcalls
    def SetInputValue(self, input_value):
        self.input_value = input_value


    def InitNorthView(self):
        """ initialize the north view
        """

        matrix = AllplanGeo.Matrix3D()

        matrix.SetRotation(AllplanGeo.Line3D(0, 0, 0, 1000, 0, 0), AllplanGeo.Angle(-math.pi/2))


    def GetAbscissaEle(self) -> (GeometryTyping.CURVES | None):
        """ get the abscissa ele

        Returns:
            abscissa element
        """

        return self.abscissa_ele


    def GetInputPlane(self) -> (AllplanGeo.Plane3D | None):
        """ get the input plane

        Returns:
            input plane
        """

        return self.input_plane


    #--------------------- mocked functions

    def GetInputViewDocument(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the input view document

        Returns:
            input view document
        """

        return self.doc


    def GetActiveViewDocument(self) -> AllplanEleAdapter.DocumentAdapter:
        """ get the active view document

        Returns:
            active view document
        """

        return self.doc


    def GetViewWorldProjection(self) -> AllplanIFW.ViewWorldProjection:
        """ get the view world projection

        Returns:
            view world projection
        """

        if not self.is_valid_doc:
            return AllplanIFW.ViewWorldProjection()

        return AllplanIFW.ViewWorldProjection.CreateForUnitTest(self.doc)


    def IsMouseMove(self,
                    message: int) -> bool:
        """ get the mouse move state

        Args:
            message: message

        Returns:
            mouse move state
        """

        return message == 512       # pylint: disable=magic-value-comparison


    def SetInputText(self,
                     _text: str):
        """ set the input text

        Args:
            _text: input test
        """


    def InitFirstPointInput(self,
                            _text            : str,
                            _coord_input_mode= 0):
        """ init the first point input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """

        self.abscissa_ele = None


    def InitNextPointInput(self, _text, _coord_input_mode = 0):
        """ init the first point input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """
        self.abscissa_ele = None


    def InitFirstElementInput(self, _text, _coord_input_mode = 0):
        """ init the first element input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """

        self.abscissa_ele = None


    def InitNextElementInput(self, _text, _coord_input_mode = 0):
        """ init the next element input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """

        self.abscissa_ele = None


    def InitFirstPointValueInput(self, _text, _value_input_control_data = 0, _coord_input_mode = 0):
        """ init the first point and value input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """

        self.abscissa_ele = None


    def InitNextPointValueInput(self, _text, _value_input_control_data = 0, _coord_input_mode = 0):
        """ init the next point and value input

        Args:
            _text:             input text
            _coord_input_mode: coordinate input mode
        """

        self.abscissa_ele = None


    def AddGeometryFromPreviewElements(self,
                                       geo_ele: Any):
        """ add the geometry from the preview element

        Args:
            geo_ele: geometry
        """


    def GetInputPoint(self,
                      _mouse_msg   : int,
                      _pnt         : AllplanGeo.Point2D,
                      _msg_info    : AllplanIFW.AddMsgInfo,
                      _start_pnt   = AllplanGeo.Point3D(),
                      _is_start_pnt= False) -> CoordinateInputResult:
        """ Get the current input point

        End point input is possible by a distance input to the start point

        Args:
            _mouse_msg:    mouse message ID
            _pnt:          input point in Allplan view coordinates
            _msg_info:     additional mouse message info
            _start_pnt:    Starting point
            _is_start_pnt: Starting point is active

        Returns:
            Current input point result
        """

        input_pnt = self.input_point

        if self.abscissa_ele:
            pnt_loc = AllplanGeo.TransformCoord.PointLocal(self.abscissa_ele, input_pnt) # type: ignore

            input_pnt = AllplanGeo.TransformCoord.PointGlobal(self.abscissa_ele, pnt_loc.X) # type: ignore

        return CoordinateInputResult(input_pnt, 0)

    def SetElementFilter(self, _selectSetting: AllplanIFW.ElementSelectFilterSetting):
        """Set the element selection filter

        Args:
            selectSetting:  Element selection filter
        """

    def SetGeometryFilter(self,
                          _geo_filter: AllplanIFW.SnoopElementGeometryFilter):
        """ Set the geometry element selection filter

        Args:
            _geo_filter: description
        """


    def GetSelectedGeometryElement(self) -> (AllplanEleAdapter.BaseElementAdapter | None):
        """ get the selected geometry element

        Returns:
            selected geometry element
        """

        return self.geo_ele


    def GetCurrentPoint(self,
                        _start_pnt   = AllplanGeo.Point3D(),
                        _is_start_pnt= False) -> CoordinateInputResult:
        """Get and mark the current input point

        Returns:
            Current input point
        """

        return CoordinateInputResult(self.input_point, 0)


    def GetInputControlValue(self) -> float :
        """Get the double value from the value input control

        Returns:
            Double value from the value input control
        """

        return self.input_value


    def IsEmptyValueInputControl(self) -> bool:
        """Check, whether there is no input inside the input control

        Returns:
            Input control is empty: true/false
        """

        is_empty = not self.SetInputValue.has_been_called

        if self.SetInputValue.has_been_called:
            self.SetInputValue(None)

        return is_empty


    def SetAbscissaElement(self,
                           curve              : GeometryTyping.CURVES,
                           _handle_to_asso_mat: Any):
        """ set the abscissa element

        Args:
            curve:               abscissa element
            _handle_to_asso_mat: handel to the asso matrix
        """

        self.abscissa_ele = curve


    def SetProjectionBase0(self,
                           set_projection_base0: bool):
        """Set the projection base of the coordinate selection

        Args:
            set_projection_base0:   True:  the input plane normal coordinate is set to 0
                                    False:: the input plane normal coordinate is used from the selected point
        """

    def SelectElement(self,
                      *_args: Any) -> bool:
        """ Select an element if no identification point exists. Use the filter set by
            SetElementFilter

        Args:
            *_args: arguments

        Returns:
            Element is selected: true false
        """

        return not self.selected_element.IsNull()


    def GetSelectedElement(self) -> AllplanEleAdapter.BaseElementAdapter:
        """Get the selected element

        The function can be used in case of eIdentMode = MODE_TEXTPOINT,
        SelectGeometryElement, SelectElement, ...

        Returns:
            Selected element
        """
        return self.selected_element


    def SetInputPlane(self,
                      plane: AllplanGeo.Plane3D):
        """Set the input plane

        The input point will be transformed to the input plane: true/false

        Args:
            plane:  Input plane
        """

        self.input_plane = plane


    def CancelInput(self):
        """Explicit cancel of the input function
        """
