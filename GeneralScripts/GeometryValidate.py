"""
Script for the error checking and trace
"""

import NemAll_Python_Geometry as AllplanGeo

def polyhedron(error_code):
    """
    Check and trace a polyhedron error

    Returns:
        True in case of no error in polyhedron creation
        False in case of error in polyhedron creation
    """

    if error_code != AllplanGeo.eGeometryErrorCode.eOK:
        print()
        print("Polyhedron is not valid: ", error_code)
        print()

        return False

    return True


def element_method(error_code):
    """
    Check and trace a element error

    Returns:
        True in case of no error in element method
        False in case of error in element method
    """

    if error_code != AllplanGeo.eGeometryErrorCode.eOK:
        print()
        print("Result of element method is not valid: ", error_code)
        print()

        return False

    return True


def offset(error_code):
    """
    Check and trace an offset error

    Returns:
        True in case of no error in offset creation
        False in case of error in offset creation
    """

    if error_code != AllplanGeo.eGeometryErrorCode.eOK:
        print()
        print("Offset is not valid: ", error_code)
        print()

        return False

    return True


def intersection(result):
    """
    Check and trace an intersection error

    Returns:
        True in case of no error in intersection creation
        False in case of error in intersection creation
    """

    if not result:
        print()
        print("Intersection is not valid:")
        print()

        return False

    return True


def is_valid(element):
    """
    Check for a valid element and trace an error

    Returns:
        True in case of valid
        False in case of not valid
    """

    if str(type(element)) == "<class 'NemAll_Python_Geometry.Polygon3D'>":
        res, state = element.IsValidStatus()

        if not res:
            print()
            print("Polygon3D is not valid: ", state)
            print()

            return False

    elif str(type(element)) == "<class 'NemAll_Python_Geometry.Polygon2D'>":
        res = element.IsValid()

        if not res:
            print()
            print("Polygon2D is not valid")
            print()

            return


    return True


