"""
Implementation of the functions for the creation of the reinforcement shapes
inside a foundation

The foundation are define by the following lines

-->source for wallfoundation
-->source for columnfoundation

                     s        e
                     |        | 
           top_line1 |        | bottom_line1
                     |        |
                     e        s   top_line2    
     e-----------------------------------------s
     s                   *                     e                    
     | top_lin3          |                     | bottom_line3
     |                   *                     |
     e                                         s
     s-----------------------------------------e
                            bottom_line2


    thr reinforcement follows the linenumbers
                     s        e
                     |        | 
                (2)  |        | (1)
                     |        |
                     e        s         (4)
     e-----------------------------------------s
     s                                       * e                    
 (6) |                                       | | (5)
     |                                       * |
     e                                         s
     s-----------------------------------------e
                                        (3)
"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
from  ModularConstructionSystem.PP_Interpret_Basics import Transform_Basics


#shape 1
def create_wallfound_shape_type_t_1_3_2(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the link shape in the foundation

                              |         |
                              | |     | |
                              | |     | |
                              | |     | |
                    |-----------|-----|-------------|
                    |           |     |             | 
                    |           |     |             |
                    |           |_____|             |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type


    """

    del top_line2 
    del bottom_line3
    del top_line3

    del hook_start_length 
    del hook_start_angle
    del hook_end_length    
    del hook_end_angle 
    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.top),
                            (top_line1, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line1, concrete_cover_props.right),
                            (concrete_cover_props.top)])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 2
def create_wallfound_shape_type_b_3(bottom_line1, 
                                    top_line1, 
                                    bottom_line2, 
                                    top_line2,
                                    bottom_line3,
                                    top_line3,
                                    shape_props, 
                                    concrete_cover_props, 
                                    start_length, 
                                    end_length,
                                    hook_start_length, 
                                    hook_start_angle,
                                    hook_end_length, 
                                    hook_end_angle,
                                    reinforcement_type
                                    ): 
    
    """
    Create the longitudinal shape in the foundation

                              |         |
                              |         |
                              |         |
                              |         |
                    |-------------------------------|
                    |                               | 
                    |                               |
                    |  ___________________________  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """
    del top_line1
    del top_line2 
    del top_line3
    del bottom_line1
    del bottom_line3

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.right),
                            (bottom_line2, concrete_cover_props.bottom),
                            (concrete_cover_props.left)])
 
    shape_builder.SetAnchorageLengthStart(start_length)
    shape_builder.SetAnchorageLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 3
def create_wallfound_shape_type_b_5_3_6(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):  
    """
    Create the longitudinal shape in the foundation

                              |         |
                              |         |
                              |         |
                              |         |
                    |-------------------------------|
                    |                               | 
                    |  |                         |  |
                    |  |_________________________|  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type

    """
    del bottom_line1 
    del top_line1
    del top_line2

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.right),
                            (top_line3, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line3, concrete_cover_props.right),
                            (concrete_cover_props.left)])

    if start_length:
        shape_builder.SetSideLengthStart(start_length)

    if end_length:
        shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 4
def create_wallfound_shape_type_b_6_3_5_4(bottom_line1, 
                                          top_line1, 
                                          bottom_line2, 
                                          top_line2,
                                          bottom_line3,
                                          top_line3,
                                          shape_props, 
                                          concrete_cover_props, 
                                          start_length, 
                                          end_length,
                                          hook_length_start, 
                                          hook_angle_start,
                                          hook_length_end, 
                                          hook_angle_end,
                                          stirrup_type
                                          ):

    """
    Create the stirrup shape in the foundation


                    |-------------------------------|
                    |  ---------------------------  | 
                    |  |                         |  |
                    |  ---------------------------  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del bottom_line1 
    del top_line1
    del start_length 
    del end_length

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.right),
                            (top_line3, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line3, concrete_cover_props.right),
                            (top_line2, concrete_cover_props.top),
                            (concrete_cover_props.left)])

    if hook_length_start > 0  and  hook_angle_start != 0:
        shape_builder.SetHookStart(hook_length_start, hook_angle_start, AllplanReinf.HookType.eStirrup)

    elif hook_length_start > 0:
        shape_builder.SetHookStart(hook_length_start, 0, AllplanReinf.HookType.eStirrup)

    if hook_length_end > 0  and  hook_angle_end != 0:
        shape_builder.SetHookEnd(hook_length_end, hook_angle_end, AllplanReinf.HookType.eStirrup)

    elif hook_length_end > 0:
        shape_builder.SetHookEnd(hook_length_end, 0, AllplanReinf.HookType.eStirrup)

    return  shape_builder.CreateStirrup(shape_props,
                                        stirrup_type)


#shape 5/1
def create_wallfound_shape_type_b_6_3_5_4_l(bottom_line1, 
                                            top_line1, 
                                            bottom_line2, 
                                            top_line2,
                                            bottom_line3,
                                            top_line3,
                                            shape_props, 
                                            concrete_cover_props, 
                                            start_length, 
                                            end_length,
                                            hook_length_start, 
                                            hook_angle_start,
                                            hook_length_end, 
                                            hook_angle_end,
                                            stirrup_type
                                            ):

    """
    Create the stirup shape in the foundation


                              |         |
                    |-------------------------------|
                    |  ------------------           | 
                    |  |                |           |
                    |  ------------------           |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            stirrup-width-bottom
                top_line2               stirrup-width-top
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                stirrup_type            reinforcement type
   """

    del bottom_line1 
    del top_line1
    del end_length

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_bottom_line2 = AllplanGeo.Line2D(bottom_line2)
    hlp_bottom_line3 = AllplanGeo.Line2D(bottom_line3)

    hlp_bottom_line2.SetEndPoint(AllplanGeo.Point2D(bottom_line2.StartPoint.X + start_length,bottom_line2.EndPoint.Y))
    hlp_bottom_line3.SetStartPoint(AllplanGeo.Point2D(hlp_bottom_line2.EndPoint))
    hlp_bottom_line3.SetEndPoint(AllplanGeo.Point2D(top_line2.EndPoint.X + start_length,top_line2.EndPoint.Y))

    shape_builder.AddSides([(concrete_cover_props.right),
                            (top_line3, concrete_cover_props.left),
                            (hlp_bottom_line2, concrete_cover_props.bottom),
                            (hlp_bottom_line3, - concrete_cover_props.right),
                            (top_line2, concrete_cover_props.top),
                            (concrete_cover_props.left)])

    if stirrup_type == AllplanReinf.StirrupType.Torsion:
        shape_builder.AddPoint(AllplanGeo.Point2D(0, width), concrete_cover_props.top, 0)

    if hook_length_start > 0  and  hook_angle_start != 0:
        shape_builder.SetHookStart(hook_length_start, hook_angle_start, AllplanReinf.HookType.eStirrup)

    elif hook_length_start > 0:
        shape_builder.SetHookStart(hook_length_start, 0, AllplanReinf.HookType.eStirrup)

    if hook_length_end > 0  and  hook_angle_end != 0:
        shape_builder.SetHookEnd(hook_length_end, hook_angle_end, AllplanReinf.HookType.eStirrup)

    elif hook_length_end > 0:
        shape_builder.SetHookEnd(hook_length_end, 0, AllplanReinf.HookType.eStirrup)

    return  shape_builder.CreateStirrup(shape_props,
                                        stirrup_type)



#shape 5/2
def create_wallfound_shape_type_b_6_3_5_4_r(bottom_line1, 
                                            top_line1, 
                                            bottom_line2, 
                                            top_line2,
                                            bottom_line3,
                                            top_line3,
                                            shape_props, 
                                            concrete_cover_props, 
                                            start_length, 
                                            end_length,
                                            hook_length_start, 
                                            hook_angle_start,
                                            hook_length_end, 
                                            hook_angle_end,
                                            stirrup_type
                                            ):

    """
    Create the stirrup shape in the foundation

                              |         |
                    |-------------------------------|
                    |         --------------------  | 
                    |         |                  |  |
                    |         --------------------  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            stirrup-width-bottom
                top_line2               stirrup-width-top
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                stirrup_type            stirrup type
    """

    del bottom_line1 
    del top_line1
    del end_length 

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    hlp_top_line2 = AllplanGeo.Line2D(top_line2)
    hlp_top_line3 = AllplanGeo.Line2D(top_line3)

    hlp_top_line2.SetEndPoint(AllplanGeo.Point2D(top_line2.StartPoint.X - start_length,top_line2.EndPoint.Y))
    hlp_top_line3.SetStartPoint(AllplanGeo.Point2D(hlp_top_line2.EndPoint))
    hlp_top_line3.SetEndPoint(AllplanGeo.Point2D(bottom_line2.EndPoint.X - start_length,bottom_line2.EndPoint.Y))

    shape_builder.AddSides([(concrete_cover_props.right),
                            (hlp_top_line3, - concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line3, concrete_cover_props.right),
                            (hlp_top_line2, concrete_cover_props.top),
                            (concrete_cover_props.left)])

    if stirrup_type == AllplanReinf.StirrupType.Torsion:
        shape_builder.AddPoint(AllplanGeo.Point2D(0, width), concrete_cover_props.top, 0)

    if hook_length_start > 0  and  hook_angle_start != 0:
        shape_builder.SetHookStart(hook_length_start, hook_angle_start, AllplanReinf.HookType.eStirrup)

    elif hook_length_start > 0:
        shape_builder.SetHookStart(hook_length_start, 0, AllplanReinf.HookType.eStirrup)

    if hook_length_end > 0  and  hook_angle_end != 0:
        shape_builder.SetHookEnd(hook_length_end, hook_angle_end, AllplanReinf.HookType.eStirrup)

    elif hook_length_end > 0:
        shape_builder.SetHookEnd(hook_length_end, 0, AllplanReinf.HookType.eStirrup)

    return  shape_builder.CreateStirrup(shape_props,
                                        stirrup_type)


#shape 6/1
def create_wallfound_shape_type_t_2_5_r(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the L-shape in the foundation

                |         |
                | |       |
                | |       |
                | |       |
                | |       |---------------------|
                | |                             | 
                | |                           | |
                | |___________________________| |
                |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del bottom_line1 
    del bottom_line3
    del top_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    if hook_start_length > 0  and  hook_start_angle != 0:
        shape_builder.SetHookStart(hook_start_length, hook_start_angle, AllplanReinf.HookType.eStirrup)

    elif hook_start_length > 0:
        shape_builder.SetHookStart(hook_start_length, 0, AllplanReinf.HookType.eStirrup)

    if hook_end_length > 0  and  hook_end_angle != 0:
        shape_builder.SetHookEnd(hook_end_length, hook_end_angle, AllplanReinf.HookType.eStirrup)

    elif hook_end_length > 0:
        shape_builder.SetHookEnd(hook_end_length, 0, AllplanReinf.HookType.eStirrup)

    shape_builder.AddSides([(concrete_cover_props.top),
                            (top_line1, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (concrete_cover_props.right)])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 6/2
def create_wallfound_shape_type_t_1_5_l(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the link shape in the foundation

                                |         |
                                |       | |
                                |       | |
                                |       | |
            |-------------------|       | |
            |                           | | 
            | |                         | |
            | |_________________________| |
            |-----------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del top_line1
    del top_line2 
    del top_line3
    del bottom_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    if hook_start_length > 0  and  hook_start_angle != 0:
        shape_builder.SetHookStart(hook_start_length, hook_start_angle, AllplanReinf.HookType.eStirrup)

    elif hook_start_length > 0:
        shape_builder.SetHookStart(hook_start_length, 0, AllplanReinf.HookType.eStirrup)

    if hook_end_length > 0  and  hook_end_angle != 0:
        shape_builder.SetHookEnd(hook_end_length, hook_end_angle, AllplanReinf.HookType.eStirrup)

    elif hook_end_length > 0:
        shape_builder.SetHookEnd(hook_end_length, 0, AllplanReinf.HookType.eStirrup)

    shape_builder.AddSides([(concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line1, concrete_cover_props.right),
                            (concrete_cover_props.top)])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 7/1
def create_wallfound_shape_type_t_1_5_r(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the L-shape in the foundation

                |         |
                |       | |
                |       | |
                |       | |
                |       | |---------------------|
                |       |                       | 
                |       |                       |
                | ______|                       |
                |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del bottom_line3
    del top_line1
    del top_line2
    del top_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    #----------------- Check the intersection point
    result, help_pnt = AllplanGeo.IntersectionCalculusEx(bottom_line1,bottom_line2)
    if not GeometryValidate.intersection(result):
        return False          
                                                       

    shape_builder.AddSides([(concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line1, concrete_cover_props.right),
                            (concrete_cover_props.top)])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 7/2
def create_wallfound_shape_type_t_2_5_l(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the link shape in the foundation

                                |         |
                                | |       |
                                | |       |
                                | |       |
            |-------------------| |       |
            |                     |       | 
            |                     |       |
            |                     |______ |
            |-----------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """
    del bottom_line1 
    del bottom_line3
    del top_line2
    del top_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    #----------------- Check the intersection point
    result, help_pnt = AllplanGeo.IntersectionCalculusEx(top_line1,bottom_line2)
    if not GeometryValidate.intersection(result):
        return False          

    shape_builder.AddSides([(concrete_cover_props.top),
                            (top_line1, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (concrete_cover_props.right)])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 7 - stripfoundation
def create_wallfound_shape_type_b_6_3_5(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_length_start, 
                                        hook_angle_start,
                                        hook_length_end, 
                                        hook_angle_end,
                                        stirrup_type
                                        ):

    """
    Create the stirrup shape in the foundation


                    |-------------------------------|
                    |  ---                     ---  | 
                    |  |                         |  |
                    |  ---------------------------  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the column
                top_line1               Top line of the column
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_length_start       start length hook
                hook_angle_start        start angle hook
                hook_length_end         end length hook
                hook_angle_end          end angle hook
                stirrup_type            stirrup type
    """

    del bottom_line1 
    del top_line1
    del top_line2
    del stirrup_type
    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(0),
                            (top_line3, concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (bottom_line3, concrete_cover_props.right),
                            (0)])

    if hook_length_start > 0  and  hook_angle_start != 0:
        shape_builder.SetHookStart(hook_length_start, hook_angle_start, AllplanReinf.HookType.eStirrup)

    elif hook_length_start > 0:
        shape_builder.SetHookStart(hook_length_start, 0, AllplanReinf.HookType.eStirrup)

    if hook_length_end > 0  and  hook_angle_end != 0:
        shape_builder.SetHookEnd(hook_length_end, hook_angle_end, AllplanReinf.HookType.eStirrup)

    elif hook_length_end > 0:
        shape_builder.SetHookEnd(hook_length_end, 0, AllplanReinf.HookType.eStirrup)

    return shape_builder.CreateShape(shape_props)  

#shape 4 - column
def create_wallfound_shape_type_t_b1_2_t1(bottom_line1,
                                          top_line1,
                                          depth, 
                                          top_line2, 
                                          bottom_line3,
                                          top_line3,
                                          shape_props, 
                                          concrete_cover_props, 
                                          start_length, 
                                          end_length,
                                          hook_length_start, 
                                          hook_angle_start,
                                          hook_length_end, 
                                          hook_angle_end,
                                          stirrup_type
                                          ):

    """
    Create the stirrup shape in the column

                       3 /--------------/ 4
                        / /----------/ /
                       / /          / / 
                      / /          / /
                     / /----------/ / 
                  2 /--------------/ 1    
             /                               /
            |-------------------------------|
            |                               | 
            |                               |

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the column
                top_line1               Top line of the column
                depth                   Column depth
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                stirrup_type            stirrup_type 
    """


    del top_line2
    del bottom_line3 
    del top_line3
    del start_length 
    del end_length

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    line1_2_4 = AllplanGeo.Line2D(AllplanGeo.Point2D(bottom_line1.StartPoint), AllplanGeo.Point2D(bottom_line1.StartPoint.X,  bottom_line1.StartPoint.Y + depth))
    line4_2_3 = AllplanGeo.Line2D(AllplanGeo.Point2D(bottom_line1.StartPoint.X, bottom_line1.StartPoint.Y + depth), AllplanGeo.Point2D(top_line1.EndPoint.X,top_line1.EndPoint.Y + depth))
    line3_2_2 = AllplanGeo.Line2D(AllplanGeo.Point2D(top_line1.EndPoint.X,top_line1.EndPoint.Y + depth), AllplanGeo.Point2D(top_line1.EndPoint))
    line2_2_1 = AllplanGeo.Line2D(AllplanGeo.Point2D(top_line1.EndPoint), AllplanGeo.Point2D(bottom_line1.StartPoint))

    shape_builder.AddSides([(0),
                            (line1_2_4, concrete_cover_props.right),
                            (line4_2_3, concrete_cover_props.bottom),
                            (line3_2_2, concrete_cover_props.left),
                            (line2_2_1, concrete_cover_props.top),
                            (0)])

    if hook_length_start > 0  and  hook_angle_start != 0:
        shape_builder.SetHookStart(hook_length_start, hook_angle_start, AllplanReinf.HookType.eStirrup)

    elif hook_length_start > 0:
        shape_builder.SetHookStart(hook_length_start, 0, AllplanReinf.HookType.eStirrup)

    if hook_length_end > 0  and  hook_angle_end != 0:
        shape_builder.SetHookEnd(hook_length_end, hook_angle_end, AllplanReinf.HookType.eStirrup)

    elif hook_length_end > 0:
        shape_builder.SetHookEnd(hook_length_end, 0, AllplanReinf.HookType.eStirrup)

    return  shape_builder.CreateStirrup(shape_props,
                                        stirrup_type)

#shape longbar
def create_longitudional_bar(z_min, z_max, place_pnt, shape_props, concrete_cover_props,
                             bottom_anchorage = 0, top_anchorage = 0):
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
    shape_pol += AllplanGeo.Point3D(place_pnt.X, place_pnt.Y, z_min + concrete_cover_props.left)
    shape_pol += AllplanGeo.Point3D(place_pnt.X, place_pnt.Y, z_max - concrete_cover_props.right)


    return AllplanReinf.BendingShape(shape_pol, AllplanUtil.VecDoubleList(),
                                     shape_props.diameter, shape_props.steel_grade,
                                     shape_props.concrete_grade,
                                     AllplanReinf.BendingShapeType.LongitudinalBar)


"""
shapes for longbars
shape7 - shape8

                     s        e
                     |        | 
           top_line1 |        | bottom_line1
                     |        |
                     e        s   top_line2    
     e-----------------------------------------s
     s                   *                     e                    
     | top_lin3          |                     | bottom_line3
     |                   *                     |
     e                                         s
     s-----------------------------------------e
                            bottom_line2


    thr reinforcement follows the linenumbers
                     s        e
                     |        | 
                (2)  |        | (1)
                     |        |
                     e        s         (4)
     e-----------------------------------------s
     s                                       * e                    
 (6) |                                       | | (5)
     |                                       * |
     e                                         s
     s-----------------------------------------e
                                        (3)
"""
#shape 8/1
def create_wallfound_shape_type_b_8_b(bottom_line1, 
                                      top_line1, 
                                      bottom_line2, 
                                      top_line2,
                                      bottom_line3,
                                      top_line3,
                                      shape_props, 
                                      concrete_cover_props, 
                                      start_length, 
                                      end_length,
                                      hook_start_length, 
                                      hook_start_angle,
                                      hook_end_length, 
                                      hook_end_angle,
                                      reinforcement_type
                                      ): 
    
    """
    Create the longitudinal shape in the foundation

                              |         |
                              |         |
                              |         |
                              |         |
                    |-------------------------------|
                    |                               | 
                    |                               |
                    |  ___________________________  |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.right),
                            (bottom_line2, concrete_cover_props.bottom),
                            (concrete_cover_props.left)])
 
    shape_builder.SetAnchorageLengthStart(start_length)
    shape_builder.SetAnchorageLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 8/2
def create_wallfound_shape_type_b_8_t(bottom_line1, 
                                      top_line1, 
                                      bottom_line2, 
                                      top_line2,
                                      bottom_line3,
                                      top_line3,
                                      shape_props, 
                                      concrete_cover_props, 
                                      start_length, 
                                      end_length,
                                      hook_start_length, 
                                      hook_start_angle,
                                      hook_end_length, 
                                      hook_end_angle,
                                      reinforcement_type
                                      ): 
    
    """
    Create the longitudinal shape in the foundation

                              |         |
                              |         |
                              |         |
                              |         |
                    |-------------------------------|
                    |  ---------------------------  | 
                    |                               | 
                    |                               |
                    |-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    shape_builder.AddSides([(concrete_cover_props.right),
                            (top_line2, concrete_cover_props.top),
                            (concrete_cover_props.left)])
 
    shape_builder.SetAnchorageLengthStart(start_length)
    shape_builder.SetAnchorageLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)

############################
#shape 10/1
def create_wallfound_shape_type_t_1_3_r(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):


    """
    Create the L-shape in the foundation

                |         |
                |       | |
                |       | |
                |       | |
        |-------|       | |---------------------|
        |       :       |                       | 
        |       :       |                       |
        |       :       |_____________________  |
        |-------:-------------------------------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del bottom_line3
    del top_line1
    del top_line2
    del top_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    err, hlp_bottom_line1 = AllplanGeo.Offset(0, bottom_line1)
    hlp_bottom_line1.Reverse()                                                                

    if hook_start_length > 0  and  hook_start_angle != 0:
        shape_builder.SetHookStart(hook_start_length, hook_start_angle, AllplanReinf.HookType.eStirrup)

    elif hook_start_length > 0:
        shape_builder.SetHookStart(hook_start_length, 0, AllplanReinf.HookType.eStirrup)

    if hook_end_length > 0  and  hook_end_angle != 0:
        shape_builder.SetHookEnd(hook_end_length, hook_end_angle, AllplanReinf.HookType.eStirrup)

    elif hook_end_length > 0:
        shape_builder.SetHookEnd(hook_end_length, 0, AllplanReinf.HookType.eStirrup)

    shape_builder.AddSides([(concrete_cover_props.top),
                            (hlp_bottom_line1, - concrete_cover_props.right),
                            (bottom_line2, concrete_cover_props.bottom),
                            (concrete_cover_props.right) ])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 10/2
def create_wallfound_shape_type_t_2_3_l(bottom_line1, 
                                        top_line1, 
                                        bottom_line2, 
                                        top_line2,
                                        bottom_line3,
                                        top_line3,
                                        shape_props, 
                                        concrete_cover_props, 
                                        start_length, 
                                        end_length,
                                        hook_start_length, 
                                        hook_start_angle,
                                        hook_end_length, 
                                        hook_end_angle,
                                        reinforcement_type
                                        ):

    """
    Create the link shape in the foundation

                                |         |
                                | |       |
                                | |       |
                                | |       |
            |-------------------| |       :-------|
            |                     |       :       |
            |                     |       :       | 
            |  ___________________|       :       |
            |-----------------------------:-------|

    Return: Bar shape in world coordinates

    Parameter:  bottom_line1            Bottom line of the wall
                top_line1               Top line of the wall
                bottom_line2            Bottom line of the strip foundation
                top_line2               Top line of the strip foundation
                bottom_line3            Left line of the strip foundation
                top_line3               Right line of the strip foundation

                shape_props             Shape properties
                concrete_cover_props    Concrete cover at the sides
                start_length            Length of the start side
                end_length              Length of the end side
                hook_start_length       start length hook
                hook_start_angle        start angle hook
                hook_end_length         end length hook
                hook_end_angle          end length angle
                reinforcement_type      reinforcement type
    """

    del bottom_line1 
    del bottom_line3
    del top_line2
    del top_line3

    del reinforcement_type

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    err, hlp_top_line1 = AllplanGeo.Offset(0, top_line1)
    hlp_top_line1.Reverse()

    if hook_start_length > 0  and  hook_start_angle != 0:
        shape_builder.SetHookStart(hook_start_length, hook_start_angle, AllplanReinf.HookType.eStirrup)

    elif hook_start_length > 0:
        shape_builder.SetHookStart(hook_start_length, 0, AllplanReinf.HookType.eStirrup)

    if hook_end_length > 0  and  hook_end_angle != 0:
        shape_builder.SetHookEnd(hook_end_length, hook_end_angle, AllplanReinf.HookType.eStirrup)

    elif hook_end_length > 0:
        shape_builder.SetHookEnd(hook_end_length, 0, AllplanReinf.HookType.eStirrup)

    shape_builder.AddSides([(concrete_cover_props.left),
                            (bottom_line2, concrete_cover_props.bottom),
                            (hlp_top_line1, - concrete_cover_props.left),
                            (concrete_cover_props.top) ])

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder.CreateShape(shape_props)


#shape 11/1+2 with shape 7


