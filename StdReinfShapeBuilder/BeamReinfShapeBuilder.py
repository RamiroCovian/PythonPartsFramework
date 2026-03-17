"""
Implementation of the functions for the creation of the reinforcement shapes inside a beam

Source for beam-shape-detection

The beam are define by the following lines

                     top_line2 (tl2)
                     e--------s
                     s        e
                     |        | 
           top_line1 |        | bottom_line1 (bl1)
           (tl2)     |        |
                     e        s      
                     s--------e
                     bottom_line2 (bl2)
                

-->the reinforcement follows the linenumbers

                         (4) 
                     e--------s
                     s        e
                     |        | 
                (1)  |        | (2)
                     |        |
                     e        s
                     s--------e
                        (3)
         
    
-->Define the Parameter: Create the link shape in the foundation

                |---------|     |---------|     |---------|
                | |     | |     | |-----| |     |||=====|||
                | |     | |     | |     | |     | |     | | 
                | |     | |     | |     | |     | |     | |
                | |_____| |     | |_____| |     | |_____| |
                |---------|     |---------|     |---------|

Return: Bar shape in world coordinates

Parameter:  bl1                 Bottom line of the beam
            tl1                 Top line of the beam
            bl2                 Bottom line of the beam
            tl2                 Top line of the beam

            sh_props            Shape properties
            coco_props          Concrete cover at the sides
            start_length        Length of the start side
            end_length          Length of the end side
            hook_length_start   Start length hook
            hook_angle_start    Start angle hook
            hook_length_end     End length hook
            hook_angle_end      End length angle
            stir_typ            Stirrup type
            stir_width          Width stirrup

"""

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
import StdReinfShapeBuilder.GeneralReinfShapeBuilder as GeneralShapeBuilder
from  ModularConstructionSystem.PP_Interpret_Basics import Transform_Basics

def create_beam_shapebuilder(start_length, 
                             end_length,
                             hook_start_length = 0., 
                             hook_start_angle = 0.,
                             hook_end_length = 0., 
                             hook_end_angle = 0.,
                            ):
    """
    Start with the shape_builder
    set the hooks, hook length
    set the side length

    Returns:
        shape_builder:    Shape Builder
    """

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()

    if hook_start_length > 0  and  hook_start_angle != 0:
        shape_builder.SetHookStart(hook_start_length, hook_start_angle, AllplanReinf.HookType.eStirrup)

    elif hook_start_length > 0:
        shape_builder.SetHookStart(hook_start_length, 0, AllplanReinf.HookType.eStirrup)

    if hook_end_length > 0  and  hook_end_angle != 0:
        shape_builder.SetHookEnd(hook_end_length, hook_end_angle, AllplanReinf.HookType.eStirrup)

    elif hook_end_length > 0:
        shape_builder.SetHookEnd(hook_end_length, 0, AllplanReinf.HookType.eStirrup)

    shape_builder.SetSideLengthStart(start_length)
    shape_builder.SetSideLengthEnd(end_length)

    return shape_builder


#shape 1 - 2-cutting ability
def create_beam_shape_type_1_3_2(**para):  

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])
 
    shape_builder.AddSides([(para["coco_props"].top), (para["tl1"], para["coco_props"].left), (para["bl2"], para["coco_props"].bottom), (para["bl1"], para["coco_props"].right), (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 4-cutting ability
# -- overlapping - fix width (2/3) -left 
def create_beam_shape_type_1_3_2__4_fix_l(**para):
                                         
    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 4-cutting ability
# -- overlapping - fix width (2/3) -right
def create_beam_shape_type_1_3_2__4_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 4-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_1_3_2__4_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 4-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_1_3_2__4_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 4-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_1_3_2__4_fix_a(**para):

    shape_builder = create_beam_shape_type_1_3_2(**para)
    
    return shape_builder
 

#shape 1 - 4-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_1_3_2__4_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - fix width (3/5) -left 
def create_beam_shape_type_1_3_2__6_fix_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_3_5 + para["coco_props"].left , para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - fix width (3/5) -middle 
def create_beam_shape_type_1_3_2__6_fix_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint  = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = top_line1_hlp.EndPoint
    bottom_line2_hlp.EndPoint   = bottom_line1_hlp.StartPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - fix width (3/5) -right 
def create_beam_shape_type_1_3_2__6_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_1_3_2__6_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - flex width -middle
def create_beam_shape_type_1_3_2__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_1_3_2__6_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_1_3_2__6_fix_a(**para):

    shape_builder = create_beam_shape_type_1_3_2(**para)
    
    return shape_builder


#shape 1 - 6-cutting ability
# -- stepping - flex width -middle
def create_beam_shape_type_1_3_2__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err, top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 1 - 6-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_1_3_2__6_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


#shape 2 - 2-cutting ability
def create_beam_shape_type_1_3_2_4(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (para["bl2"], para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 4-cutting ability
# -- overlapping - fix width (2/3) -left 
def create_beam_shape_type_1_3_2_4__4_fix_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 4-cutting ability
# -- overlapping - fix width (2/3) -right
def create_beam_shape_type_1_3_2_4__4_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 4-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_1_3_2_4__4_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))
    
    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 4-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_1_3_2_4__4_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 4-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_1_3_2_4__4_fix_a(**para):

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder = create_beam_shape_type_1_3_2_4(**para)

    return shape_builder


#shape 2 - 4-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_1_3_2_4__4_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - fix width (3/5) -left 
def create_beam_shape_type_1_3_2_4__6_fix_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_3_5 + para["coco_props"].left , para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - fix width (3/5) -middle 
def create_beam_shape_type_1_3_2_4__6_fix_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = top_line1_hlp.EndPoint
    bottom_line2_hlp.EndPoint   = bottom_line1_hlp.StartPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - fix width (3/5) -right 
def create_beam_shape_type_1_3_2_4__6_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_1_3_2_4__6_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - flex width -middle
def create_beam_shape_type_1_3_2_4__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_1_3_2_4__6_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_1_3_2_4__6_fix_a(**para):
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder = create_beam_shape_type_1_3_2_4(**para)

    return shape_builder


#shape 2 - 6-cutting ability
# -- stepping - flex width -middle
def create_beam_shape_type_1_3_2_4__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist = AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 2 - 6-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_1_3_2_4__6_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].top)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 2-cutting ability
def create_beam_shape_type_4_1_3_2_4(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (para["bl2"], para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 4-cutting ability
# -- overlapping - fix width (2/3) -left 
def create_beam_shape_type_4_1_3_2_4__4_fix_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_3 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 4-cutting ability
# -- overlapping - fix width (2/3) -right
def create_beam_shape_type_4_1_3_2_4__4_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_1_3 = width_tmp / 3. 
    width_2_3 = width_tmp / 3. * 2.

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_1_3 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 4-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_4_1_3_2_4__4_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))
    
    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 4-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_4_1_3_2_4__4_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 4-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_4_1_3_2_4__4_fix_a(**para):

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder = create_beam_shape_type_4_1_3_2_4(**para)

    return shape_builder


#shape 3 - 4-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_4_1_3_2_4__4_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - fix width (3/5) -left 
def create_beam_shape_type_4_1_3_2_4__6_fix_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_2_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_3_5 + para["coco_props"].left , para["bl2"].EndPoint.Y )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - fix width (3/5) -middle 
def create_beam_shape_type_4_1_3_2_4__6_fix_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_1_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].StartPoint.X - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - width_1_5 - para["coco_props"].right - para["sh_props"].diameter /2., para["bl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = top_line1_hlp.EndPoint
    bottom_line2_hlp.EndPoint   = bottom_line1_hlp.StartPoint

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - fix width (3/5) -right 
def create_beam_shape_type_4_1_3_2_4__6_fix_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    width_tmp =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint)) - para["coco_props"].left - para["coco_props"].right - para["sh_props"].diameter
    width_3_5 = width_tmp / 5. * 3. 
    width_2_5 = width_tmp / 5. * 2.
    width_1_5 = width_tmp / 5. 

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["tl1"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].StartPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["tl1"].EndPoint.X   + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["tl1"].EndPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(para["bl2"].StartPoint.X + width_2_5 + para["coco_props"].left + para["sh_props"].diameter /2., para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - flex width -left
def create_beam_shape_type_4_1_3_2_4__6_free_l(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = para["bl2"].StartPoint
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(para["bl2"].StartPoint.X + para["stir_width"] + para["coco_props"].left - para["sh_props"].diameter / 2., para["bl2"].EndPoint.Y )

    bottom_line1_hlp = AllplanGeo.Line2D()
    bottom_line1_hlp.StartPoint = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].StartPoint.Y)
    bottom_line1_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line2_hlp.EndPoint.X , para["bl1"].EndPoint.Y)

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["tl1"], para["coco_props"].left),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - flex width -middle
def create_beam_shape_type_4_1_3_2_4__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- overlapping - flex width -right
def create_beam_shape_type_4_1_3_2_4__6_free_r(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])

    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    top_line1_hlp = AllplanGeo.Line2D()
    top_line1_hlp.StartPoint = AllplanGeo.Point2D(para["bl1"].EndPoint.X   - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].EndPoint.Y)
    top_line1_hlp.EndPoint   = AllplanGeo.Point2D(para["bl1"].StartPoint.X - para["stir_width"] - para["coco_props"].right + para["sh_props"].diameter / 2., para["bl1"].StartPoint.Y)

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint.X , para["bl2"].EndPoint.Y )
    bottom_line2_hlp.EndPoint   = para["bl2"].EndPoint

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (para["bl1"], para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- stepping - fix width -outside
def create_beam_shape_type_4_1_3_2_4__6_fix_a(**para):
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    shape_builder = create_beam_shape_type_4_1_3_2_4(**para)

    return shape_builder


#shape 3 - 6-cutting ability
# -- stepping - flex width -middle
def create_beam_shape_type_4_1_3_2_4__6_free_m(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist = AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 3 - 6-cutting ability
# -- stepping - flex width -inside
def create_beam_shape_type_4_1_3_2_4__6_free_i(**para):

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"], para["hook_length_start"], para["hook_angle_start"], para["hook_length_end"], para["hook_angle_end"])
    
    if para["start_length"] > 0. and para["end_length"] > 0.:
        para["tl2"].SetStartPoint(AllplanGeo.Point2D(para["tl2"].StartPoint.X,para["start_length"]))
        para["tl2"].SetEndPoint(AllplanGeo.Point2D(para["tl2"].EndPoint.X,para["start_length"]))

    # ermittlung mittellinie
    center_line_dist = AllplanGeo.Point2D()
    center_line_dist =  AllplanGeo.Point2D.GetDistance(AllplanGeo.Point2D(para["bl2"].StartPoint), AllplanGeo.Point2D(para["bl2"].EndPoint))

    center_line_b1_t1 = AllplanGeo.Line2D(para["bl1"])
    center_line_b1_t1.Reverse()

    center_line = AllplanGeo.Line2D()
    err,center_line = AllplanGeo.Offset(- center_line_dist / 2., center_line_b1_t1)

    err,top_line1_hlp = AllplanGeo.Offset(- para["stir_width"] / 2. + para["sh_props"].diameter / 2., center_line)

    err, bottom_line1_hlp = AllplanGeo.Offset(  para["stir_width"] / 2. - para["sh_props"].diameter / 2., center_line)
    bottom_line1_hlp.Reverse()

    bottom_line2_hlp = AllplanGeo.Line2D()
    bottom_line2_hlp.StartPoint = AllplanGeo.Point2D(top_line1_hlp.EndPoint)
    bottom_line2_hlp.EndPoint   = AllplanGeo.Point2D(bottom_line1_hlp.StartPoint )

    shape_builder.AddSides([(para["coco_props"].right),
                            (para["tl2"], para["coco_props"].top),
                            (top_line1_hlp, 0),
                            (bottom_line2_hlp, para["coco_props"].bottom),
                            (bottom_line1_hlp, 0),
                            (para["tl2"], para["coco_props"].top),
                            (para["coco_props"].left)])

    return  shape_builder.CreateStirrup(para["sh_props"], para["stir_typ"])


#shape 4 - 2-cutting ability - cup-stirrup
def create_beam_shape_type_2_4_1(**para):  

    shape_builder = create_beam_shapebuilder(para["start_length"], para["end_length"])
 
    shape_builder.AddSides([(para["coco_props"].top), (para["bl1"], para["coco_props"].right), (para["tl2"], para["coco_props"].top), (para["tl1"], para["coco_props"].left), (para["coco_props"].top)])

    return shape_builder.CreateShape(para["sh_props"])


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
                top_anchorage         Anchorage length at the top point, 0 = no
    """

    shape_pol = AllplanGeo.Polyline3D()
    shape_pol += AllplanGeo.Point3D(place_pnt.X, place_pnt.Y, z_min + concrete_cover_props.left)
    shape_pol += AllplanGeo.Point3D(place_pnt.X, place_pnt.Y, z_max - concrete_cover_props.right)

    return AllplanReinf.BendingShape(shape_pol, AllplanUtil.VecDoubleList(),
                                     shape_props.diameter, shape_props.steel_grade,
                                     shape_props.concrete_grade,
                                     AllplanReinf.BendingShapeType.LongitudinalBar)

###############
# for columns #
###############

def create_longitudinal_shape_with_user_hooks_anchorage_cranced(
                                                                shape_top,
                                                                shape_bottom,
                                                                length, 
                                                                place_pnt,
                                                                model_angles,
                                                                shape_props,
                                                                concrete_cover_props,
                                                                cropped_length = 0.,
                                                                cropped_with = 0.,
                                                                barlength_on_top = 0.,
                                                                start_hook       = 0,
                                                                end_hook         = 0,
                                                                start_hook_angle = 90.0,
                                                                end_hook_angle   = 90.0,
                                                                hook_type_start  = -1,
                                                                hook_type_end    = -1,
                                                                start_anchorage  = 0.,
                                                                end_anchorage    = 0.
                                                                ):
    """
    Create a longitudinal shape with user defined hooks, anchorage, crank

    Return: Bar shape of the longitudinal shape in world coordinates

    Parameter:  
                shape_top                   Bending shape on top
                                            0-straight / 1-cranked / 2-curved
                shape_bottom                Bending shape on bottom
                                            0-straight / 2-curved
                length                      Length of the geometry side
                place_pnt                   global input point (Placementpoint)
                model_angles                Angles for the local to global shape transformation
                shape_props                 Shape properties
                concrete_cover_props        Concrete cover properties: needed left, right, bottom
                cropped_length              cropped length
                cropped_with                cropped with
                barlength_on_top            bar length after cropping to the top
                start_hook                  Create a hook at the start point:
                                            -1 = no / 0 = calculate / >0 = value
                end_hook                    Create a hook at the end point:
                                            -1 = no / 0 = calculate / >0 = value
                start_hook_angle            Create a hook with specified angle [-180, 180]:
                                            default is 90°
                end_hook_angle              Create a hook with specified angle [-180, 180]:
                                            default is 90°
                hook_type_start             Type of the hook at the start point, -1 set type from angle
                hook_type_end               Type of the hook at the end point, -1 set type from angle
                start_anchorage             Anchorage length at the start point, 0 = no
                end_anchorage               Anchorage length at the end point, 0= no

                cranking:
                  | 4. point
                  |
                 /  3.
                /
                |   2.
                |
                |   1.

                start--> Bottom / end-->Top
    """

    shape_builder = AllplanReinf.ReinforcementShapeBuilder()
    if shape_top == 1:
        #when cranking --> no hooks on top
        end_hook = -1

    if shape_bottom == 0:
        #when strait --> no hooks on bottom
        start_hook = -1

    if shape_top == 0:
        #when strait --> no hooks on top
        end_hook = -1

    if shape_top == 1: #cranked
        if barlength_on_top >= 0:
            shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),                                                                 
                                        (AllplanGeo.Point2D(length - cropped_length - barlength_on_top, 0), concrete_cover_props.bottom),               
                                        (AllplanGeo.Point2D(length - barlength_on_top, cropped_with), concrete_cover_props.bottom),                     
                                        (AllplanGeo.Point2D(length , cropped_with), concrete_cover_props.bottom),                                        
                                        (concrete_cover_props.right)])
        else:
           shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),                                                                 
                                        (AllplanGeo.Point2D(length - barlength_on_top, 0), concrete_cover_props.bottom),               
                                        (AllplanGeo.Point2D(length - barlength_on_top + cropped_length, cropped_with), concrete_cover_props.bottom),                     
                                        (AllplanGeo.Point2D(length - barlength_on_top + cropped_length + 1., cropped_with), concrete_cover_props.bottom),
                                        (concrete_cover_props.right)])

    else:
        shape_builder.AddPoints([(AllplanGeo.Point2D(), concrete_cover_props.left),
                                 (AllplanGeo.Point2D(length, 0), concrete_cover_props.bottom),
                                 (concrete_cover_props.right)])


    if start_hook >= 0:
        shape_builder.SetHookStart(start_hook, start_hook_angle,
                                   GeneralShapeBuilder.get_hook_type_from_angle(hook_type_start, start_hook_angle))

    if end_hook >= 0:
        shape_builder.SetHookEnd(end_hook, end_hook_angle,
                                 GeneralShapeBuilder.get_hook_type_from_angle(hook_type_end, end_hook_angle))


    if start_anchorage != 0:
        shape_builder.SetAnchorageLengthStart(start_anchorage)

    if end_anchorage != 0:
        shape_builder.SetAnchorageLengthEnd(end_anchorage)

    shape = shape_builder.CreateShape(shape_props)


    #----------------- Rotate the shape to the model

    if shape.IsValid() is True:
        shape.Rotate(model_angles)

    if shape.IsValid() is True:
        shape.Move(AllplanGeo.Vector3D(place_pnt.X, place_pnt.Y, place_pnt.Z))

    return shape

