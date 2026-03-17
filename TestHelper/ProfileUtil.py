""" Implementation of the profile utilities
"""

# pylint: disable=import-error
# pylint: disable=bare-except
# pylint: disable=import-outside-toplevel
# pylint: disable=consider-using-with
# pylint: disable=global-statement

from __future__ import annotations

from typing import Callable, Any

import cProfile
import pstats
import os
import subprocess
import builtins
import enum

import NemAll_Python_Utility as AllplanUtil


#----------------- import the profiler if possible

try:
    from line_profiler import LineProfiler

    builtins.line_profiler = LineProfiler()       # type: ignore

    def use_line_profiler(mod: Any) -> Any:
        """ implementation of the line usage function

        Args:
            mod: module to add

        Returns:
            result of the executed function
        """

        builtins.line_profiler.add_module(mod)              # type: ignore

        from inspect import isfunction

        if isfunction(mod):
            builtins.line_profiler.add_function(mod)        # type: ignore
        else:
            builtins.line_profiler.add_module(mod)          # type: ignore

        def function_wrapper(*args) -> Any:
            """ function wrapper for the line profiled

            Args:
                *args: arguments of the function

            Returns:
                function result
            """
            if args:
                result = mod(*args)
            else:
                result = mod()

            return result

        return function_wrapper

    builtins.use_line_profiler = use_line_profiler  # type: ignore

except:
    pass


class ProfilerType(enum.IntEnum):
    """ Definition of profiler types """

    C_PROFILE     = 1
    PY_INSTRUMENT = 2
    LINE_PROFILER = 3
    AUSTIN        = 4


class ProfileUtil():
    """ Profiler utility class """

    @staticmethod
    def __profile_by_cprofile(function              : Callable,
                              calls_to_print        : int,
                              show_graphical_results: bool,
                              *param                : Any):
        """ profile by cprofile

        Args:
            function:               function to execute
            calls_to_print:         number of calls shown in the profile report
            show_graphical_results: show graphical results
            param:                  parameter for the function
        """

        profiler = cProfile.Profile(timeunit = 1000)
        profiler.enable()

        if param:
            if str(function).find("create_interactor") == -1:
                ret_value = function(*param)
            else:
                ret_value = function(*param, print_script_name = False)
        else:
            ret_value = function()

        profiler.disable()

        profiler.create_stats()

        stats = pstats.Stats(profiler)

        stats.strip_dirs()

        stats.sort_stats('cumtime')
        stats.print_stats(calls_to_print)

        if not show_graphical_results:
            return ret_value

        tmp_path = os.environ['TMP'].split(os.pathsep)[0]

        profiler.dump_stats(tmp_path + "\\Profile.pstat")

        try:
            import gprof2dot

        except:
            AllplanUtil.ShowMessageBox("Module gprof2dot.py must be available in\n\n...\\Prg\\Python\\lib\\site-packages",
                                       AllplanUtil.MB_OK)

            return ret_value

        gprof2dot.main(["-f", "pstats", "-n", "1", tmp_path + "\\Profile.pstat", "-o", tmp_path + "\\Profile.dot"])

        graphviz = "C:\\Program Files\\Graphviz\\bin\\dot.exe"

        if not os.path.exists(graphviz):
            AllplanUtil.ShowMessageBox("The Graphviz software must be installed",
                                       AllplanUtil.MB_OK)

            return ret_value

        subprocess.run(graphviz + " " + tmp_path + "\\Profile.dot -Tsvg -o "+ tmp_path + "\\Profile.svg",
                       check = False)

        chrome = "C:\\Program Files\\Google\\Chrome\\Application\\Chrome.exe"

        if not os.path.exists(graphviz):
            AllplanUtil.ShowMessageBox("The Chrome software is not found in " + chrome,
                                       AllplanUtil.MB_OK)

            return ret_value

        subprocess.Popen(chrome + " " + tmp_path + "\\Profile.svg")

        return ret_value


    @staticmethod
    def __profile_by_pyinstrument(function, *param):
        """ profile by pyinstrument

        Args:
            function:   function to execute
            *param:      parameter for the function
        """

        try:
            from pyinstrument.profiler import Profiler

        except:
            AllplanUtil.ShowMessageBox("Module folder pyinstrument must be available in\n\n...\\Prg\\Python\\lib\\site-packages",
                                       AllplanUtil.MB_OK)

            if param:
                return function(*param)

            return function()


        #----------------- execute the profiling

        profiler = Profiler()
        profiler.start()

        if param:
            ret_value = function(*param)
        else:
            ret_value = function()

        profiler.stop()

        profiler.output_html()

        profiler.open_in_browser()

        return ret_value


    @staticmethod
    def __profile_by_line_profiler(function, *param):
        """ profile by line_profiler

        Args:
            function:   function to execute
            *param:      parameter for the function
        """

        if not builtins.line_profiler:  # type: ignore
            AllplanUtil.ShowMessageBox("Module folder line_profiler must be available in\n\n...\\Prg\\Python\\lib\\site-packages",
                                       AllplanUtil.MB_OK)

            if param:
                return function(*param)

            return function()


        #----------------- execute the line profiling

        builtins.line_profiler.enable_by_count()    # type: ignore

        if param:
            ret_value = function(*param)
        else:
            ret_value = function()

        builtins.line_profiler.print_stats(output_unit = 0.001, stripzeros = True)  # type: ignore

        builtins.line_profiler.disable_by_count()   # type: ignore

        return ret_value


    @staticmethod
    def profile(function              : Callable,
                *param                : Any,
                calls_to_print        : int          = 20,
                description           : str          = "",
                show_graphical_results: bool         = False,
                profiler_type         : ProfilerType = ProfilerType.C_PROFILE,
                show_separator_line   : bool         = False,
                result_file_name      : str          = "") -> Any:
        """ profile by cprofile

        Args:
            function:               function to execute
            *param:                 function parameter
            calls_to_print:         number of calls shown in the profile report (only for C_Profile)
            description:            description of the text
            show_graphical_results: show graphical results (only for C_Profile)
            profiler_type:          type of the profiler
            show_separator_line:    show a separator line before the results
            result_file_name:       name of the result file

        Returns:
            return value of the call function
        """

        if show_separator_line:
            print()
            print()
            print("=======================================================================================================================")

        if description:
            print()
            print(description + ":")
            print("-" * (len(description) + 1))
            print()
            print()

        print("---------------------------")
        print("---------------------------")
        print(profiler_type)
        print("---------------------------")
        print("---------------------------")
        print("---------------------------")

        if profiler_type == ProfilerType.C_PROFILE:
            return ProfileUtil.__profile_by_cprofile(function, calls_to_print, show_graphical_results, *param)

        if profiler_type == ProfilerType.PY_INSTRUMENT:
            return ProfileUtil.__profile_by_pyinstrument(function, *param)

        if profiler_type == ProfilerType.LINE_PROFILER:
            return ProfileUtil.__profile_by_line_profiler(function, *param)

        if profiler_type == ProfilerType.AUSTIN:
            from TestHelper.ProfileUtilAustin import profile_by_austin

            return profile_by_austin(result_file_name, function, *param)

        print()
        print()
        print()
        print()
        print("Wrong profiler set!!!")

        return ""
