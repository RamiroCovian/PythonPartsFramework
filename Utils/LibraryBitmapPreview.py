""" Implementation of the library bitmap preview """

from typing import Any, List

import os
import struct

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BasisElements as AllplanBasisEle

from TestHelper import PythonPartPylintDecorator

@PythonPartPylintDecorator.deprecated(replace = "use create_library_bitmap_preview(...)")
def create_libary_bitmap_preview(png_file_name: str) -> List[Any]:
    """ deprecated function with typo

    Args:
        png_file_name: pnt file name

    Returns:
        list with the model elements for the preview
    """

    return create_library_bitmap_preview(png_file_name)


UNPACK_CODE = 0x0d0a1a0a


def create_library_bitmap_preview(png_file_name: str) -> List[Any]:
    """ This function creates the preview objects, which are needed to draw
    a bitmap inside the preview window of the library

    Args:
        png_file_name: full name of the png file

    Returns:
        list with the model elements for the preview
    """

    if not os.path.isfile(png_file_name):
        print("")
        print("")
        print("file " + png_file_name + " not found for the library preview!!!")
        print("")
        print("")
        return []


    #----------------- read the size

    width  = 1000
    height = 1000

    with open(png_file_name, 'rb') as fhandle:
        head = fhandle.read(24)

        if struct.unpack('>i', head[4:8])[0] == UNPACK_CODE:
            width, height = struct.unpack('>ii', head[16:24])

        fhandle.close()


    #------------------ Define the polygon

    polygon = AllplanGeo.Polygon2D()
    polygon += AllplanGeo.Point2D(0,0)
    polygon += AllplanGeo.Point2D(width,0)
    polygon += AllplanGeo.Point2D(width,height)
    polygon += AllplanGeo.Point2D(0,height)
    polygon += AllplanGeo.Point2D(0,0)


    #------------------ Define common properties, take global Allplan settings

    com_prop = AllplanBaseEle.CommonProperties()
    com_prop.GetGlobalProperties()


    #------------------ Define BitmapArea properties

    bitmaparea_prop            = AllplanBasisEle.BitmapAreaProperties()
    bitmaparea_prop.BitmapName = png_file_name


    #------------------ Append for creation as new Allplan elements

    return [AllplanBasisEle.BitmapAreaElement(com_prop, bitmaparea_prop, polygon)]
