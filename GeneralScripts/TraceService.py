"""
Implementation of the trace utilities
"""

# pylint: disable=invalid-name
# pylint: disable=protected-access

import string
import enum

import NemAll_Python_AllplanSettings as AllplanSettings

class TraceLevel(enum.IntEnum):
    """
    Definition of the trace levels
    """

    PYP_FILE_NAME      = 1
    STRING_TABLE_NAME  = 2
    SCRIPT_NAME        = 3
    LANGUAGE_FILE_NAME = 4
    VS_NODE_LOAD_INFO  = 5
    FAVORITE_FILE_NAME = 6
    MISSING_TEXT_ID    = 7


class TraceService:
    """
    Definition of service class TraceService
    """

    class __TraceService():
        """ implementation of the internal class """

        def __init__(self):
            """ read the data """

            self.trace_level_dict = {}

            file_name = AllplanSettings.AllplanPaths.GetUsrPath() + "PythonPartTraceLevel.dat"

            try:
                with open(file_name, 'r', encoding="utf8") as file:
                    for line in file.readlines():
                        name, _, value = line.partition("=")

                        self.trace_level_dict[getattr(TraceLevel, name, None)] = value.strip(" \n") == "True"

            except FileNotFoundError:
                return


        def trace(self, trace_level, *args):
            """ trace the arguments """

            if not trace_level in self.trace_level_dict:
                return

            if not self.trace_level_dict[trace_level]:
                return

            print(*[TraceService.__make_trace_readable(arg) for arg in args])


        def set_trace_missing_text_id(self, trace_state: bool):
            """ set the trace state for a missing text id"""

            self.trace_level_dict[TraceLevel.MISSING_TEXT_ID] = trace_state


    #----------------- access to the internal implementation

    instance = None

    def __init__(self, reset = False):
        if reset or not TraceService.instance:
            TraceService.instance = TraceService.__TraceService()

        self.instance = TraceService.instance


    def __getattr__(self, name):
        return getattr(self.instance, name)


    @staticmethod
    def __make_trace_readable(input_str):
        """
        Converts a string in trace readable signs

        Args:
            input_str    :input string to convert

        Returns: string with replaced non ascii signs
        42LäLöLß62 will be converted to 42L?L?L?62
        """

        res =''

        for char in input_str:
            if char not in string.printable:
                if char.isnumeric():
                    res += char
                else:
                    res += '?'# sign char is not trace readable
            else:
                res += char

        return res


    @staticmethod
    def trace_1(value):
        """
        Converts signs in value to printable, if necessary and prints value

        Arg:    value string to print into trace
        """

        strtmp = TraceService.__make_trace_readable(value)
        print(strtmp)


    @staticmethod
    def trace_2(strvalue_front, strvalue_back):
        """
        If necessary converts signs in strvalue_front and strvalue_back to printable and prints both

        Arg:    value string to print into trace
        """

        strtmp_back  = TraceService.__make_trace_readable(strvalue_back)
        strtmp_front = TraceService.__make_trace_readable(strvalue_front)

        print(strtmp_front, strtmp_back)
