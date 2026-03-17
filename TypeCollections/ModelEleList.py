""" implementation of the model element list
"""

from typing import get_args

import NemAll_Python_AllplanSettings as AllplanSettings
import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_BasisElements as AllplanBasisEle
import NemAll_Python_Geometry as AllplanGeo

from .Curve3DList import Curve3DList

ModelEle2D = (AllplanGeo.Line2D | AllplanGeo.Arc2D |
              AllplanGeo.Polyline2D | AllplanGeo.Polygon2D |
              AllplanGeo.Spline2D | AllplanGeo.BSpline2D |
              AllplanGeo.Path2D | AllplanGeo.Clothoid2D)

ModelEle3D = (AllplanGeo.Line3D | AllplanGeo.Arc3D |
              AllplanGeo.Polyline3D | AllplanGeo.Polygon3D |
              AllplanGeo.Polyhedron3D | AllplanGeo.BRep3D |
              AllplanGeo.Spline3D | AllplanGeo.BSpline3D |
              AllplanGeo.Path3D |
              AllplanGeo.Cylinder3D | AllplanGeo.ExtrudedAreaSolid3D |
              AllplanGeo.ClippedSweptSolid3D | AllplanGeo.Cuboid3D)

ListModelEle2D = (list[AllplanGeo.Line2D] | list[AllplanGeo.Arc2D] |
                  list[AllplanGeo.Polyline2D] | list[AllplanGeo.Polygon2D] |
                  list[AllplanGeo.Spline2D] | list[AllplanGeo.BSpline2D] |
                  list[AllplanGeo.Path2D] | list[AllplanGeo.Clothoid2D])

ListModelEle3D = (list[AllplanGeo.Line3D] | list[AllplanGeo.Arc3D] |
                  list[AllplanGeo.Polyline3D] | list[AllplanGeo.Polygon3D] |
                  list[AllplanGeo.Polyhedron3D] | list[AllplanGeo.BRep3D] |
                  list[AllplanGeo.Spline3D] | list[AllplanGeo.BSpline3D] |
                  list[AllplanGeo.Path3D] |
                  list[AllplanGeo.Cylinder3D] | list[AllplanGeo.ExtrudedAreaSolid3D] |
                  list[AllplanGeo.ClippedSweptSolid3D] | list[AllplanGeo.Cuboid3D])

ModelEle2DList = (AllplanGeo.Line2DList | AllplanGeo.Arc2DList |
                  AllplanGeo.Polyline2DList | AllplanGeo.Polygon2DList |
                  AllplanGeo.Spline2DList | AllplanGeo.BSpline2DList |
                  AllplanGeo.Path2DList | AllplanGeo.Clothoid2D)

ModelEle3DList = (AllplanGeo.Line3DList | AllplanGeo.Arc3DList |
                  AllplanGeo.Polyline3DList | AllplanGeo.Polygon3DList |
                  AllplanGeo.Polyhedron3DList | AllplanGeo.BRep3DList |
                  AllplanGeo.Spline3DList | AllplanGeo.BSpline3DList |
                  AllplanGeo.Path3DList |
                  AllplanGeo.Cylinder3DList | AllplanGeo.ExtrudedAreaSolid3DList |
                  AllplanGeo.ClippedSweptSolid3DList | AllplanGeo.Cuboid3DList)

class ModelEleList(list):
    """ implementation of the model element list
    """

    def __init__(self,
                 com_prop: AllplanBaseEle.CommonProperties = AllplanSettings.AllplanGlobalSettings.GetCurrentCommonProperties()):
        """ initialize

        Args:
            com_prop: common properties for the elements
        """

        self.__com_prop = AllplanBaseEle.CommonProperties(com_prop)


    def append_geometry_2d(self,
                           geo_ele : (ListModelEle2D | ModelEle2D | ModelEle2DList),
                           com_prop: (AllplanBaseEle.CommonProperties | None) = None):
        """ append a 2D geometry element to the list

        Args:
            geo_ele:  2D geometry element
            com_prop: common properties
        """

        if isinstance(geo_ele, get_args(ModelEle2D)):
            self.append(AllplanBasisEle.ModelElement2D(self.__com_prop if com_prop is None else com_prop, geo_ele))
        else:
            self += [AllplanBasisEle.ModelElement2D(self.__com_prop if com_prop is None else com_prop, item) \
                     for item in geo_ele] # type: ignore


    def append_geometry_3d_with_texture(self,
                                        geo_ele    : (ListModelEle3D | ModelEle3D | ModelEle3DList | Curve3DList),
                                        texture_def: AllplanBasisEle.TextureDefinition,
                                        com_prop   : (AllplanBaseEle.CommonProperties | None) = None):
        """ append a 3D geometry element to the list

        Args:
            geo_ele:     3D geometry element
            texture_def: texture definition
            com_prop:    common properties
        """

        if isinstance(geo_ele, get_args(ModelEle3D)):
            self.append(AllplanBasisEle.ModelElement3D(self.__com_prop if com_prop is None else com_prop,
                                                       texture_def, geo_ele))
        else:
            self += [AllplanBasisEle.ModelElement3D(self.__com_prop if com_prop is None else com_prop,
                                                    texture_def, item) \
                    for item in geo_ele] # type: ignore


    def append_geometry_3d(self,
                           geo_ele : (ListModelEle3D | ModelEle3D | ModelEle3DList | Curve3DList),
                           com_prop: (AllplanBaseEle.CommonProperties | None) = None):
        """ append a 3D geometry element to the list

        Args:
            geo_ele:  3D geometry element
            com_prop: common properties
        """

        if isinstance(geo_ele, get_args(ModelEle3D)):
            self.append(AllplanBasisEle.ModelElement3D(self.__com_prop if com_prop is None else com_prop, geo_ele))
        else:
            self += [AllplanBasisEle.ModelElement3D(self.__com_prop if com_prop is None else com_prop, item) \
                     for item in geo_ele] # type: ignore


    def set_color(self,
                  color: int):
        """ set the color

        Args:
            color: color
        """

        self.__com_prop.Color = color

    def set_pen(self,
                pen: int):
        """ set the pen

        Args:
            pen: pen
        """

        self.__com_prop.Pen = pen

    def set_stroke(self,
                   stroke: int):
        """ set the stroke

        Args:
            stroke: stroke
        """

        self.__com_prop.Stroke = stroke

    def set_common_properties(self,
                              com_prop: AllplanBaseEle.CommonProperties):
        """ set the common properties

        Args:
            com_prop: common properties
        """

        self.__com_prop = com_prop

    def set_element_attributes(self,
                               index     : int,
                               attributes: list[AllplanBaseEle.Attribute]):
        """ set the attributes to the element with the defined index

        Args:
            index:      index
            attributes: attributes
        """

        self[index].Attributes = AllplanBaseEle.Attributes([AllplanBaseEle.AttributeSet(attributes)])

    def __getitem__(self,
                    index: int) -> AllplanBasisEle.AllplanElement:
        """ get the model element by an index

        Args:
            index: index

        Returns:
            model element as AllplanElement
        """

        return super().__getitem__(index)
