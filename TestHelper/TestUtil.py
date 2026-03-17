"""
Implementation of the test utilities
"""

import unittest
import difflib
import subprocess
import codecs

from typing import List

from itertools import takewhile

from BuildingElementGeometryUtil import BuildingElementGeometryUtil

import NemAll_Python_Geometry as AllplanGeo

class PrintError(unittest.TestCase):
    """ helper class """

    def __init__(self,
                 new_text    : str,
                 indent_count: int):
        """ initialize

        Args:
            new_text:     new element text
            indent_count: indent count
        """

        self.new_text = new_text
        self.indent   = " " * indent_count

        super().__init__()


    def copy_text_to_clipboard(self):
        """ copy the text to the clipboard
        """

        text = self.new_text.replace("\\", "\\\\")

        result_text = ""

        for item in text.split("\n"):
            if self.indent:
                result_text += self.indent + "\"" + item.replace("\"", "\\\"") + "\\n\"    \\\n"
            else:
                result_text += item.replace("\"", "\\\"") + "\n"

        if result_text:
            subprocess.run(['clip.exe'], input = result_text.strip(" \\\n").encode("UTF-8"), check=True)


    def execute(self,
                ele1_str: str,
                ele2_str: str,
                str1    : str,
                str2    : str,
                info_str= ""):
        """ execute the assert

        Args:
            ele1_str: strings from the first element
            ele2_str: strings from the second element
            str1:     row string from the first element
            str2:     row string from the second element
            info_str: info string
        """

        text1 = ele1_str.splitlines()
        text2 = ele2_str.splitlines()

        diff = difflib.unified_diff(text1, text2)

        diff_str = "\n".join(diff)

        print(diff_str)

        self.copy_text_to_clipboard()

        self.fail("\n\n" + info_str + "\n\n" + "Different values in line:\n" + str1 + "\n" + str2 + "\n")


    def print_msg(self,
                  msg     : str,
                  set_fail: bool = True):
        """ print a message

        Args:
            msg:      message
            set_fail: set fail state
        """

        self.copy_text_to_clipboard()

        if set_fail:
            self.fail(f"\n\n{msg}\n")
        else:
            print(f"\n\n{msg}\n")


def compare_file_with_text(file_name   : str,
                           text        : str,
                           indent_count: int = 41):
    """ Compare a file with a text

    Args:
        file_name:    name of the file
        text:         text
        indent_count: indent count
    """

    #For searching errors enable the next 3 lines
    #print("********************************")
    #print(text)
    #print("********************************")

    with codecs.open(file_name, 'r', encoding='utf8') as file:
        file_list = file.read().splitlines()

    text_list = text.split("\n")

    error_str = ""

    file_len = len(file_list)
    text_len = len(text_list)

    for i in range(0, max(file_len, text_len)):
        if i >= file_len:
            if text_list[i]:
                error_str += "line " + str(i + 1) + "=\"" + text_list[i] + "\" is missing in the file " + file_name + "\n"

        elif i >= text_len:
            error_str += "line " + str(i + 1) + " is no more created: " + file_list[i] + "\n"

        elif file_list[i] != text_list[i]:
            file_text = file_list[i].replace("-0,","0,")
            text_text = text_list[i].replace("-0,","0,")


            #----------------- remove a path

            if file_text.find(":\\") != -1:
                file_text = file_text[file_text.rfind("\\"):]

            if text_text.find(":\\") != -1:
                text_text = text_text[text_text.rfind("\\"):]

            if file_text != text_text:
                error_str += "line " + str(i + 1) + " is different: '" + file_list[i] + "'  !=   '" + text_list[i] + "'\n"

    if not error_str:
        return ""

    print_error = PrintError("\n".join(text_list), indent_count)

    print_error.print_msg(error_str)

    return error_str


def __compare_geometry(type_name, str1, str2):
    """ check for geometry type and compare if exist """

    function_get_value = "get_value_" + type_name.lower()

    geo_fct = getattr(BuildingElementGeometryUtil, function_get_value, None)

    if not geo_fct:
        return None

    val1 = geo_fct(str1)
    val2 = geo_fct(str2)

    eps  = AllplanGeo.GetRelativeTolerance()

    if type_name == "Matrix3D":
        result = next((False for i in range(12) if not AllplanGeo.Comparison.Equal(val1[i], val2[i], eps)), True)

        if result:
            result = next((False for i in range(12, 16) if not AllplanGeo.Comparison.Equal(val1[i], val2[i], eps)), True)

        if result:
            return True

    elif AllplanGeo.Comparison.Equal(val1, val2, eps):
        return True

    return False



def compare_element_strings(ele1_str    : str,
                            ele2_str    : str,
                            indent_count: int  = 41,
                            compare_text: bool = False):
    """ Compare two element string with "real value compare

    Args:
        ele1_str:     string from the first element
        ele2_str:     string from the second element
        indent_count: indent count
        compare_text: compare the text left from the =
    """

    ele1_str = ele1_str.strip()
    ele2_str = ele2_str.strip()

    if ele1_str == ele2_str:
        return True

    print_error = PrintError(ele1_str, indent_count)

    if sum(1 for _ in takewhile(lambda c: c == '[', ele1_str)) != sum(1 for _ in takewhile(lambda c: c == '[', ele2_str)):
        print_error.execute(ele1_str, ele2_str, ele1_str[:10] + "...", ele2_str[:10] + "...")

    ele1_str = ele1_str.replace("[", "").replace("]", "").replace("\"", "'")
    ele2_str = ele2_str.replace("[", "").replace("]", "").replace("\"", "'")

    ele1_str = ele1_str.rstrip("\n")
    ele2_str = ele2_str.rstrip("\n")

    ele1_str = ele1_str.replace("), Point3D(", ")\nPoint3D(")
    ele2_str = ele2_str.replace("), Point3D(", ")\nPoint3D(")

    ele1_str = ele1_str.replace("), Vector3D(", ")\nVector3D(")
    ele2_str = ele2_str.replace("), Vector3D(", ")\nVector3D(")

    ele1_str_list = ele1_str.split("\n")
    ele2_str_list = ele2_str.split("\n")

    if len(ele1_str_list) != len(ele2_str_list):
        print("Line count new = " + str(len(ele1_str_list)))
        print("Line count old = " + str(len(ele2_str_list)))

        line_count = 1

        for str1, str2 in zip(ele1_str_list, ele2_str_list):
            if str1.split("=")[0] != str2.split("=")[0]:
                print_error.execute(ele1_str, ele2_str, str1, str2, "The item count is different in line " + str(line_count) + ":")

                return False

            line_count += 1

        print_error.print_msg("The length of the lists is different")


    #----------------- compare each line

    eps  = AllplanGeo.GetRelativeTolerance() * 10

    is_points = False

    line_index = 0

    while line_index < len(ele1_str_list):
        str1 = ele1_str_list[line_index].strip()
        str2 = ele2_str_list[line_index].strip()

        line_index += 1

        str1_org = str1
        str2_org = str2

        if str1_org.startswith("UUID=") and str2_org.startswith("UUID="):
            continue

        if str1.find("=[") != -1:
            str1 = str1[str1.find("=[") + 2:].rstrip("]").replace(";","\n")
            str2 = str2[str2.find("=[") + 2:].rstrip("]").replace(";","\n")

            if str1 or str2:
                compare_element_strings(str1, str2)

            continue

        if str1.find("&#xA") != -1:
            str1 = str1.replace("&#xA","\n")
            str2 = str2.replace("&#xA","\n")

            if str1 or str2:
                compare_element_strings(str1, str2)

            continue

        if str1.startswith("Vertices("):
            line_index = compare_vertices(line_index, ele1_str_list, ele2_str_list, print_error)

            continue


        #----------------- set the geometry type depending on the key word

        for repl_data in (("CenterPoint(", "Point3D("),
                          ("X Direction(", "Vector3D("),
                          ("Normal(",      "Vector3D("),
                          ("XDirection(", "Vector3D("),
                          ("Z Direction(", "Vector3D("),
                          ("StartVector(", "Vector3D("),
                          ("EndVector(", "Vector3D(")):
            if str1_org.find(repl_data[0]) != -1:
                str1_org = str1_org.replace(repl_data[0], repl_data[1])
                str2_org = str2_org.replace(repl_data[0], repl_data[1])


        #----------------- set the Points state

        ip1 = str1.find("(")

        if str1.startswith("Points("):
            is_points = True

        elif ip1 != -1  and  str1[0: ip1].strip():
            is_points = False

        if str1 == str2:
            continue


        #----------------- check for geometry types in one line

        ip_equal = str1.find("=")

        if ip_equal != -1:
            geo_type = str1[ip_equal + 1:]

            ip_type = geo_type.find("(")

            if ip_type > 0:
                geo_type = geo_type[:ip_type]

                res = True

                for geo_str1, geo_str2 in zip(str1[ip_equal + 1:].split(";"), str2[ip_equal + 1:].split(";")):
                    res = __compare_geometry(geo_type, geo_str1, geo_str2)

                    if res is None:
                        break

                    if res is False:
                        print_error.execute(ele1_str, ele2_str, str1_org, str2_org)
                        return False

                if res is True:
                    continue


        #----------------- compare the character before (

        ip2 = str2.find("(")

        if ip1 != ip2:
            print_error.execute(ele1_str, ele2_str, str1_org, str2_org)

            return False

        if str1.find("=Point2D") != -1 or str1.find("=Vector3D") != -1:
            is_points = True

        if ip1 == -1 and ip2 == -1:
            ip1 = str1.find("=")
            ip2 = str2.find("=")

        if compare_text and str1[:ip1] != str2[:ip2]:
            print_error.execute(ele1_str, ele2_str, str1_org, str2_org)

            return False

        str1 = str1[ip1 + 1:]
        str2 = str2[ip2 + 1:]


        #----------------- add the point type

        type_name = ""

        if is_points:
            if str1.count(",") == 1:
                str1      = "Point2D(" + str1
                str2      = "Point2D(" + str2
                type_name = "Point2D"
            else:
                str1      = "Point3D(" + str1
                str2      = "Point3D(" + str2
                type_name = "Point3D"


        #----------------- check values from geometry types

        if str1.find(")") != -1:
            str1 = str1[0: str1.find(")") + 1]
            str2 = str2[0: str2.find(")") + 1]

        if not type_name:
            type_name = str1_org[0: str1_org.rfind ("(")].strip("[")

            ip_type = type_name.rfind(" ")

            if ip_type != -1:
                type_name = type_name[ip_type + 1:]

        ip_type = type_name.find("(")

        if ip_type != -1:
            type_name = type_name[ip_type + 1:]

        res = __compare_geometry(type_name, str1, str2)

        if res is False:
            print_error.execute(ele1_str, ele2_str, str1_org, str2_org)

        if res is True:
            continue

        if type_name.find("_library=") != -1:
            continue


        #----------------- Test real values
        if type_name == "angle" or type_name.lower().startswith("angle="):
            str1 = str1[str1.find("(") + 1:].strip(")")
            str2 = str2[str2.find("(") + 1:].strip(")")

            if not AllplanGeo.Comparison.Equal(float(str1), float(str2), eps) and \
               not AllplanGeo.Comparison.Equal(float(str1) + 360., float(str2), eps) and \
               not AllplanGeo.Comparison.Equal(float(str1) - 360., float(str2), eps):
                print_error.execute(ele1_str, ele2_str, str1_org, str2_org)

        else:
            if str1.find(".") != -1  or  str2.find(".") != -1:
                str1 = str1.strip(")")
                str2 = str2.strip(")")

                for sub_str1, sub_str2 in zip(str1.split(","), str2.split(",")):
                    if sub_str1.find(";") != -1:
                        print_error.execute(ele1_str, ele2_str, str1_org, str2_org, "Line " + str(line_index + 1) + ":")

                    val1 = float(sub_str1)

                    if not AllplanGeo.Comparison.Equal(val1, float(sub_str2), abs(val1) * 1.0e-10 if abs(val1) > 1 else 1.0e-10):
                        print_error.execute(ele1_str, ele2_str, str1_org, str2_org, "Line " + str(line_index + 1) + ":")

                continue

            print_error.execute(ele1_str, ele2_str, str1_org, str2_org, "Line " + str(line_index + 1) + ":")

    return True


def compare_vertices(line_index1  : int,
                     ele1_str_list: List[str],
                     ele2_str_list: List[str],
                     print_error  : PrintError) -> int:
    """ compare the vertices """

    start_index2 = line_index1
    is_new_order = False

    while line_index1 < len(ele1_str_list):
        ele1_str = ele1_str_list[line_index1].strip().split(")")[0]

        if not ele1_str.startswith("("):
            _, _, right1 = ele1_str_list[line_index1 - 1].partition(")")
            _, _, right2 = ele2_str_list[line_index1 - 1].partition(")")

            if right1 != right2:
                print_error.print_msg("Different value in line " + ele1_str_list[line_index1 - 1])

            if is_new_order:
                print_error.print_msg("The vertices have a new order: please update the test file", False)  # release/debug problem

            return line_index1

        found = False


        #----------------- search the vertex in the second list

        for line_index2 in range(start_index2, len(ele2_str_list)):
            ele2_str = ele2_str_list[line_index2].strip().split(")")[0]

            if ele2_str.endswith(("(")):
                break

            if __compare_geometry("point3d", ele1_str, ele2_str):
                found = True

                if line_index2 == start_index2:
                    start_index2 += 1
                else:
                    is_new_order = True

                break

            line_index2 += 1

        if not found:
            print_error.execute(ele1_str, ele2_str_list[start_index2], ele1_str, ele2_str_list[start_index2])

        line_index1 += 1

    if is_new_order:
        print_error.print_msg("The vertices have a new order: please update the test file", False)    # release/debug problem

    return line_index1


def print_compare_string(compare_string):
    """
    Print a string for the test data compare

    Args:
        data_string    data string
    """

    text = "\"" + str(compare_string).replace("\n","\\n\"    \\\n                                         \"")

    print(text)

    subprocess.run(['clip.exe'], input = text.strip().encode("UTF-8"), check=True)


def get_handle_string(build_ele_list):
    """
    Get the handle string from the building element list

    Args:
        build_ele_list    building element list
    """

    node_string = ""

    for build_ele in build_ele_list:
        node_handles = getattr(build_ele, "node_handles", None)

        if node_handles:
            node_string += str(node_handles)

    return node_string
