""" implementation of the unit test runner utilities
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=c-extension-no-member

from __future__ import annotations

from typing import Optional, List, cast

import sys
import os
import unittest
import inspect

class UnitTestRunnerUtil():
    """ implementation of the unit test runner utilities """

    @staticmethod
    def init_sys_path(test_project_path: str) -> (object > None):
        """ initialize the sys path

        Args:
            test_project_path: path of the test project

        Returns:
            code coverage object
        """

        script_path = next(path for path in sys.path if path.endswith(r"\PythonPartsFramework")).rsplit("\\", 1)[0] + "\\"

        drive_letter = os.getcwd()[:3]

        is_coverage = False

        site_packages_path = ""

        if len(sys.argv) > 1:
            for path in sys.argv[1:]:
                if path == "coverage":
                    is_coverage = True
                else:
                    app_path = path if path[1] == ":" else os.getcwd()[0: 2] + path

                    sys.path.append(app_path)

                    if "prg" in app_path.lower():
                        site_packages_path = app_path


        #----------------- add the script paths

        if site_packages_path:
            sys.path.append(site_packages_path + "\\Python\\lib\\site-packages")
        else:
            sys.path.append(drive_letter + "External_AddOns\\Python\\lib\\site-packages")

        sys.path.append(script_path + 'PythonPartsFramework')
        sys.path.append(script_path + 'PythonPartsFramework\\GeneralScripts')
        sys.path.append(script_path + 'PythonPartsScripts')
        sys.path.append(script_path + 'PythonPartsExampleScripts')
        sys.path.append(script_path + 'VisualScripts')
        sys.path.append(script_path + 'VisualScripts\\NodeLib\\Classic Library')
        sys.path.append(script_path + 'VisualScripts\\NodeLib\\Deprecated Library')
        sys.path.append(script_path + 'VisualScripts\\NodeLib\\Modernized Library')
        sys.path.append(drive_letter + "NemAll_Python\\" + test_project_path)

        print()
        print(sys.path)
        print(sys.version)


        #----------------- check for code coverage

        code_coverage = None

        if is_coverage:
            import coverage

            code_coverage = coverage.Coverage()
            code_coverage.start()


        #----------------- use the global string tables

        from BuildingElementStringTableManager import BuildingElementStringTableManager

        BuildingElementStringTableManager.get_instance().set_use_global_string_table(True)

        return code_coverage


    @staticmethod
    def init_unit_test(load_resources: bool) -> object:
        """ initialize the unit test

        Args:
            load_resources: load the resources

        Returns:
            Allplan document
        """

        import NemAll_Python_Utility as AllplanUtility
        import NemAll_Python_Reinforcement as AllplanReinf

        if load_resources:
            import NemAll_Python_AllplanSettings as AllplanSettings

            import clr


            #----------------- Load the assemblies with the full path (search path is later assigned to Python.exe path)

            debug = next((True for path in sys.path if path.lower().find("debug") != -1), False)

            clr.AddReference(AllplanSettings.AllplanPaths.GetPathOfApplication() + "\\NemAll_AttribDef.dll")

            if debug:
                clr.AddReference(AllplanSettings.AllplanPaths.GetPathOfApplication() + "\\NemAll_DataWrapperD.dll")
            else:
                clr.AddReference(AllplanSettings.AllplanPaths.GetPathOfApplication() + "\\NemAll_DataWrapper.dll")


            #----------------- use the global string tables

            from BuildingElementStringTableManager import BuildingElementStringTableManager

            BuildingElementStringTableManager.get_instance().set_use_global_string_table(True)


        #----------------- initialize the unit tests and then PythonParts framework

        doc = AllplanUtility.InitUnitTest(load_resources)

        AllplanReinf.InitUnitTest()

        from TypeCollections.ModificationElementList import ModificationElementList

        from DocumentManager import DocumentManager

        DocumentManager.get_instance().document = doc
        DocumentManager.get_instance().set_pythonpart_element(ModificationElementList())


        #--------------------- set the import hook

        from ImportHook import ImportHookFinder

        sys.meta_path.append(ImportHookFinder)

        return doc


    @staticmethod
    def unload_modules(test_project_path: str):
        """ remove the test project path

        Args:
            test_project_path: path of the test project
        """

        drive_letter = os.getcwd()[:3]

        if (path := drive_letter + "NemAll_Python\\" + test_project_path) in sys.path:
            sys.path.remove(path)

        while True:
            deleted = False

            for module, _ in sys.modules.items():
                if module.find("TestNode") != -1:
                    del sys.modules[module]
                    deleted = True
                    break

            if not deleted:
                break

    @staticmethod
    def run_unit_tests(tests        : List[unittest.TestSuite],
                       code_coverage: object,
                       doc          : object,
                       single_test  : object = None) -> unittest.TestResult:
        """ run the unit tests

        Args:
            tests:         description
            code_coverage: description
            doc:           document of the Allplan drawing files
            single_test:   description

        Returns:
            test result
        """

        all_suites = unittest.TestSuite()


        #----------------- local function for adding a test to the test suites

        def add_test(item):
            if (suite := getattr(item, "suite", None)) is None:
                return

            suite_args = inspect.getfullargspec(suite)

            if suite_args.args:
                all_suites.addTest(suite(doc))
            else:
                all_suites.addTest(suite())


        #----------------- single test

        if single_test is not None:
            add_test(single_test)


        #----------------- get all imported tests

        else:
            for test in tests:
                add_test(test)


        #----------------- run the tests

        runner = unittest.TextTestRunner()

        results = runner.run(all_suites)

        if code_coverage:
            import coverage

            code_coverage = cast(coverage.Coverage, code_coverage)

            code_coverage.stop()
            code_coverage.save()

            code_coverage.html_report()

        return results
