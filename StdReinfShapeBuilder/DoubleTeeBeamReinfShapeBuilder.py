"""
Implementation of the functions for the creation of the reinforcement shapes
inside a doubleteebeam

The doubleteebeam are define by the following lines

                        1
   1.________________________________________0.
   2|                                        | 12
 ...|____     ______________________     ____|          
       3 |   |         7            |   | 11            
         |   |                      |   |               
       4 |   | 6                  8 |   | 10            
         |___|                      |___|               
           5                          9

        1 -  top_line  
        2 -  right_flange_line      
        3 -  right_flange_base_line
        4 -  right_stem_right_line 
        5 -  right_stem_base_line 
        6 -  right_stem_left_line  
        7 -  flange_base_line     
        8 -  left_stem_right_line  
        9 -  left_stem_base_line   
        10 - left_stem_left_line  
        11 - left_flange_base_line 
        12 - left_flange_line      
        (but linecounter start from 0 !)   
        sense of direction: clockwise
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder

def create_doubletee_beam_shape_type_4(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         |   |                      |   | 
         |   |                      |   |
       4 |   |                      |   |  
         |___|                      |___|
                                     

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt = AllplanGeo.Point3D(AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(3)))
    hlp_pnt.X = AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(3)).X
    hlp_pnt.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)).Y

    shape_builder.AddSides([(concrete_cover_props.bottom),
                            (AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(3)), hlp_pnt, concrete_cover_props.left),
                            (concrete_cover_props.top)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


def create_doubletee_beam_shape_type_10(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         |   |                      |   | 
         |   |                      |   |
         |   |                      |   |  10 
         |___|                      |___|
                                     

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt = AllplanGeo.Point3D(AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(9)))
    hlp_pnt.X = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(9)).X
    hlp_pnt.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)).Y

    shape_builder.AddSides([(concrete_cover_props.top),
                            (hlp_pnt, AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(9)), concrete_cover_props.left),
                            (concrete_cover_props.bottom)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


def create_doubletee_beam_shape_type_6(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         |   |                      |   | 
         |   |                      |   |
         |   | 6                    |   |   
         |___|                      |___|
                                     

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt = AllplanGeo.Point3D(AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(5)))
    hlp_pnt.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)).Y

    shape_builder.AddSides([(concrete_cover_props.top),
                            (hlp_pnt, AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(5)), concrete_cover_props.left),
                            (concrete_cover_props.bottom)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


def create_doubletee_beam_shape_type_8(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         |   |                      |   | 
         |   |                      |   |
         |   |                   8  |   |   
         |___|                      |___|
                                     

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt = AllplanGeo.Point3D(AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(7)))
    hlp_pnt.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)).Y

    shape_builder.AddSides([(concrete_cover_props.bottom),
                  #          (hlp_pnt, AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(7)), - concrete_cover_props.left),
                             (AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(7)),hlp_pnt, concrete_cover_props.left),
                            (concrete_cover_props.top)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

def create_doubletee_beam_shape_type_1(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
                       1
     ________________________________________
    |                                        | 
    |                                        |          


    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.left),
                            (AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(0)),AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)), concrete_cover_props.top),
                            (concrete_cover_props.right)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


def create_doubletee_beam_shape_type_3_7_11(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
                        
     ________________________________________
    |                                        | 
    |____     ______________________     ____|          
       3 |   |         7            |   | 11         


    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt_start = AllplanGeo.Point3D(AllplanGeo.Line3D.GetEndPoint(reinf_line.GetLine(0)))
    hlp_pnt_start.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(3)).Y
    hlp_pnt_end = AllplanGeo.Point3D(AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(0)))
    hlp_pnt_end.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(3)).Y

    shape_builder.AddSides([(concrete_cover_props.left),
                            (hlp_pnt_start, hlp_pnt_end, - concrete_cover_props.bottom),
                            (concrete_cover_props.right)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


def create_longitudional_bar(z_min, z_max, place_pnt, shape_props, concrete_cover_props):

    """
    Create the longitudinal bar

    Return: Bar shape in world coordinates

    Parameter:  z_min                 Minimal z coordinate of the geometry
                z_max                 Maximal z coordinate of the geometry
                shape_props           Shape properties
                concrete_cover_props  Concrete cover at the sides
                bottom_anchorage      Anchorage length at the bottom point, 0 = no
                top_anchorage         Anchorage length at the top point, 0= no
    """

    shape_pol = AllplanGeo.Polyline3D()
    shape_pol += AllplanGeo.Point3D(z_min + concrete_cover_props.left,  0., place_pnt.Y)
    shape_pol += AllplanGeo.Point3D(z_max - concrete_cover_props.right, 0., place_pnt.Y)

    return AllplanReinf.BendingShape(shape_pol, AllplanUtil.VecDoubleList(),
                                     shape_props.diameter, shape_props.steel_grade,
                                     shape_props.concrete_grade,
                                     AllplanReinf.BendingShapeType.LongitudinalBar)

    
def create_longitudional_bar_free(start_pnt, end_pnt, shape_props, concrete_cover_props):

    """
    Create the longitudinal bar with workplace coordinates

    Return: Bar shape in world coordinates

    Parameter:  start_pnt             Startpoint bar
                end_pnt               Endpoint bar
                shape_props           Shape properties
                concrete_cover_props  Concrete cover at the sides
    """

    shape_pol = AllplanGeo.Polyline3D()
    shape_pol += AllplanGeo.Point3D(start_pnt)
    shape_pol += AllplanGeo.Point3D(end_pnt)

    return AllplanReinf.BendingShape(shape_pol, AllplanUtil.VecDoubleList(),
                                     shape_props.diameter, shape_props.steel_grade,
                                     shape_props.concrete_grade,
                                     AllplanReinf.BendingShapeType.LongitudinalBar)

    
def create_long_bar(z_min, z_max, place_pnt, shape_props, concrete_cover_props):

    """
    Create the longitudinal bar

    Return: Bar shape in world coordinates

    Parameter:  z_min                 Minimal z coordinate of the geometry
                z_max                 Maximal z coordinate of the geometry
                shape_props           Shape properties
                concrete_cover_props  Concrete cover at the sides
                bottom_anchorage      Anchorage length at the bottom point, 0 = no
                top_anchorage         Anchorage length at the top point, 0= no
    """

    shape_pol = AllplanGeo.Polyline3D()
    shape_pol += AllplanGeo.Point3D(z_min + concrete_cover_props.left,  place_pnt.Y, place_pnt.Z)
    shape_pol += AllplanGeo.Point3D(z_max - concrete_cover_props.right, place_pnt.Y, place_pnt.Z)

    return AllplanReinf.BendingShape(shape_pol, AllplanUtil.VecDoubleList(),
                                     shape_props.diameter, shape_props.steel_grade,
                                     shape_props.concrete_grade,
                                     AllplanReinf.BendingShapeType.LongitudinalBar)

##########################
# shapes for tendon-bars #
##########################
def create_doubletee_beam_shape_type_4_6_m(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         | + |                      | + | 
         | + |                      | + |
       4 | + | 6                  8 | + | 10 
         |_+_|                      |_+_|
           5                          9

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt_start = AllplanGeo.Point3D(AllplanGeo.Line3D.GetCenterPoint(reinf_line.GetLine(4)))

    hlp_pnt_end = AllplanGeo.Point3D()
    hlp_pnt_end.X = hlp_pnt_start.X
    hlp_pnt_end.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(2)).Y

    shape_builder.AddSides([(0),
                            (hlp_pnt_start, hlp_pnt_end, concrete_cover_props.left),
                            (0)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

def create_doubletee_beam_shape_type_8_10_m(profile_reinf, model_angles, shape_props, concrete_cover_props):

    """
         | + |                      | + | 
         | + |                      | + |
       4 | + | 6                  8 | + | 10 
         |_+_|                      |_+_|
           5                          9

    Return: Bar shape in world coordinates

    Parameter:  profile_reinf           Geometry points of the warped slab
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides

    """

    reinf_line  = AllplanGeo.Polyline3D()
    reinf_line  = profile_reinf.DefinitionPoints()

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_pnt_start = AllplanGeo.Point3D(AllplanGeo.Line3D.GetCenterPoint(reinf_line.GetLine(8)))

    hlp_pnt_end = AllplanGeo.Point3D()
    hlp_pnt_end.X = hlp_pnt_start.X
    hlp_pnt_end.Y = AllplanGeo.Line3D.GetStartPoint(reinf_line.GetLine(7)).Y

    shape_builder.AddSides([(0),
                            (hlp_pnt_start, hlp_pnt_end, concrete_cover_props.left),
                            (0)])

    shape = shape_builder.CreateShape(shape_props)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape


###########################
# shapes for stem-notches #
###########################

"""
Implementation of the functions for the creation of the reinforcement shapes
inside a doubletee beam

The walls are define by the following points
              
  0            0 
  --------------
  |               
 2---3           
     |          
     -----------
     4         5
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate

#shape 1+2+5: link shape
def create_doubletee_shape_stem_type_0_1_2_3(points, model_angles,
                                        shape_props, concrete_cover_props,
                                        start_length, end_length):
    """                                                     
      1        0  
      se-------s 
      |       
      es-------e
      2       3
    Return: Bar shape in world coordinates

    Parameter:  points                  Geometry points of the stairs
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
    """
    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.top),
                            (points[0], points[1], concrete_cover_props.top),
                            (points[1], points[2], concrete_cover_props.left),
                            (points[2], points[3], concrete_cover_props.bottom),
                            (concrete_cover_props.bottom)])

    if start_length:
        shape_builder.SetSideLengthStart(start_length)

    if end_length:
        shape_builder.SetSideLengthEnd(end_length)

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model
    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape



def create_doubletee_shape_stem_longbar_hor(points, model_angles,
                                            shape_props, concrete_cover_props, dummy1, dummy2):
    """                                                     
      1        0 
      e--------s 
      |       
      ---------
   
    Return: Bar shape in world coordinates

    Parameter:  points                  Geometry points of the stem
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
    """
    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(0.),
                            (points[0], points[1], concrete_cover_props.top),
                            (0.)])

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model
    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

def create_doubletee_shape_stem_longbar_ver(points, model_angles,
                                            shape_props, concrete_cover_props, dummy1, dummy2):
    """                                                     
      0         
      s-------- 
      |       
      e--------
      1
    Return: Bar shape in world coordinates

    Parameter:  points                  Geometry points of the stem
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
    """
    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.top),
                            (points[0], points[1], 0.),
                            (concrete_cover_props.bottom)])

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model
    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

def create_doubletee_shape_stem_stirrup_ver(points, model_angles,
                                            shape_props, concrete_cover_props, dummy1, dummy2):
    """    |                                                
      2    v    1
      ---------- 
      |        |
      |        |
       |      |
       |      |
        |    |
        |    |
      3 ------ 4
      
    Return: Bar shape in world coordinates

    Parameter:  points                  Geometry points of the stem
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
    """


    shape = GeneralShapeBuilder.create_freeform_shape_with_hooks(points,
                                                                 model_angles,
                                                                 shape_props,
                                                                 concrete_cover_props.top)

    return shape

def create_doubletee_shape_stem_shear_loop(points, model_angles,
                                            shape_props, concrete_cover_props, dummy1, dummy2):
    """    |                                                
      2    v    1
      ---------- 
      |        |
      |        |
       |      |
       |      |
        |    |
        |    |
      3 ------ 4
      
    Return: Bar shape in world coordinates

    Parameter:  points                  Geometry points of the stem
                model_angles            Angles for the local to global shape transformation
                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
    """

    # complete geometry incl. coco + dm/2.
    shape_pol = AllplanGeo.Polyline3D()
    for point in points:
        shape_pol += AllplanGeo.Point3D(point)

    br_list = AllplanUtil.VecDoubleList()
    br_list[:] = [shape_props.bending_roller] * (len(points) -2) 

    shape = AllplanReinf.BendingShape(shape_pol, br_list, shape_props.diameter, shape_props.steel_grade, -1,
                                      AllplanReinf.BendingShapeType.Freeform)

    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    return shape

