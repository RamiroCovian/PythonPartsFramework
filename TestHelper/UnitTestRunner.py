""" Implementation of the unit test runner
"""

# pylint: disable=import-outside-toplevel
# pylint: disable=wrong-import-position

from __future__ import annotations

from typing import cast

from collections.abc import Callable

import sys

from unittest import mock

from TestHelper.UnitTestRunnerUtil import UnitTestRunnerUtil

def execute_tests(unit_test_fct : Callable,
                  module_name   : str,
                  load_resources: bool) -> bool:
    """ run the unit tests

    Args:
        unit_test_fct:  unit test function
        module_name:    module name
        load_resources: load the resources state

    Returns:
        test result state
    """

    code_coverage = UnitTestRunnerUtil.init_sys_path(module_name)


    #--------------------- initialize the unit test first (init Allplan data)

    #                      the NemAll_Python_BaseElements import is used to load the needed Allplan libraries before the unit test init

    import NemAll_Python_BaseElements                                   # pylint: disable=unused-import
    import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter

    from TestHelper.Mock.AllplanPathsMock import AllplanPathsMock

    script_path = next(path for path in sys.path if path.endswith(r"\PythonPartsFramework")).rsplit("\\", 1)[0] + "\\"

    @mock.patch("NemAll_Python_AllplanSettings.AllplanPaths", new = AllplanPathsMock(script_path))

    def __init_unit_test(load_resources: bool) -> AllplanEleAdapter.DocumentAdapter:
        """ initialize the unit tests

        Args:
            load_resources: load the resources state

        Returns:
            _description_
        """

        return cast(AllplanEleAdapter.DocumentAdapter, UnitTestRunnerUtil.init_unit_test(load_resources))

    doc = __init_unit_test(load_resources)


    #----------------- Mock some classes for the test execution

    from TestHelper.Mock.AttributeDataManagerMock import AttributeDataManagerMock
    from TestHelper.Mock.BuildingElementInputControlsMock import BuildingElementInputControlsMock
    from TestHelper.Mock.CreateElementsMock import CreateElementsMock
    from TestHelper.Mock.CreatePrecastElementsMock import CreatePrecastElementsMock
    from TestHelper.Mock.CreateSectionsAndViewsMock import CreateSectionsAndViewsMock
    from TestHelper.Mock.DialogFunctionsMocks import OpenAttributeSelectionDialog, OpenRGBColorDialog, OpenSymbolDialog
    from TestHelper.Mock.DrawElementPreviewMock import DrawElementPreviewMock
    from TestHelper.Mock.GeneralModificationsMock import DeleteElementsMock
    from TestHelper.Mock.HandleServiceMock import HandleServiceMock
    from TestHelper.Mock.InputFunctionStarterMock import InputFunctionStarterMock
    from TestHelper.Mock.InputFunctionStarterMock import PostElementSelectionMock
    from TestHelper.Mock.PolygonInputMock import PolygonInputMock
    from TestHelper.Mock.PolylineInputMock import PolylineInputMock
    from TestHelper.Mock.PreviewSymbolBuilderMock import PreviewSymbolBuilderMock
    from TestHelper.Mock.PythonWpfPaletteMock import PythonWpfPaletteMock
    from TestHelper.Mock.ReinforcementUtilMock import ReinforcementUtilMock
    from TestHelper.Mock.UndoRedoServiceMock import UndoRedoServiceMock

    @mock.patch("NemAll_Python_Palette.PythonWpfPalette", new = PythonWpfPaletteMock)
    @mock.patch("NemAll_Python_BaseElements.CreateElements", new = CreateElementsMock)
    @mock.patch("NemAll_Python_BaseElements.CreateSectionsAndViews", new = CreateSectionsAndViewsMock)
    @mock.patch("NemAll_Python_BaseElements.DrawElementPreview", new = DrawElementPreviewMock)
    @mock.patch("NemAll_Python_BaseElements.AttributeService.OpenAttributeSelectionDialog", new = OpenAttributeSelectionDialog)
    @mock.patch("NemAll_Python_BasisElements.BasisPropertyDialogs.OpenRGBColorDialog", new = OpenRGBColorDialog)
    @mock.patch("NemAll_Python_ArchElements.PropertyDialogs.OpenSymbolDialog", new = OpenSymbolDialog)
    @mock.patch("NemAll_Python_Precast.CreatePrecastElements", new = CreatePrecastElementsMock)
    @mock.patch("NemAll_Python_AllplanSettings.AllplanPaths", new = AllplanPathsMock(script_path))
    @mock.patch("NemAll_Python_IFW_Input.PreviewSymbolBuilder", new = PreviewSymbolBuilderMock)
    @mock.patch("NemAll_Python_IFW_Input.HandleService", new = HandleServiceMock)
    @mock.patch("NemAll_Python_IFW_Input.BuildingElementInputControls", new = BuildingElementInputControlsMock)
    @mock.patch("NemAll_Python_IFW_Input.PostElementSelection", new = PostElementSelectionMock)
    @mock.patch("NemAll_Python_IFW_Input.InputFunctionStarter", new = InputFunctionStarterMock)
    @mock.patch("NemAll_Python_IFW_Input.UndoRedoService", new = UndoRedoServiceMock)
    @mock.patch("NemAll_Python_IFW_Input.PolygonInput", new = PolygonInputMock)
    @mock.patch("NemAll_Python_IFW_Input.PolylineInput", new = PolylineInputMock)
    @mock.patch("NemAll_Python_BaseElements.AttributeDataManager", new = AttributeDataManagerMock)
    @mock.patch("NemAll_Python_BaseElements.DeleteElements", new = DeleteElementsMock)

    @mock.patch("NemAll_Python_Reinforcement.ReinforcementUtil.GetNextBarPositionNumber",
                new = ReinforcementUtilMock.GetNextBarPositionNumber)
    @mock.patch("NemAll_Python_Reinforcement.ReinforcementUtil.GetNextMeshPositionNumber",
                new = ReinforcementUtilMock.GetNextMeshPositionNumber)

    def __execute_tests(unit_test_fct: Callable,
                        code_coverage: bool,
                        doc          : AllplanEleAdapter.DocumentAdapter) -> bool:
        """ execute the unit tests

        Args:
            unit_test_fct: unit test function
            code_coverage: code coverage state
            doc:           document of the Allplan drawing files

        Returns:
            test result state
        """

        results = unit_test_fct(doc, code_coverage)

        return not results.wasSuccessful()


    #--------------------- execute the tests

    result = __execute_tests(unit_test_fct, code_coverage, doc)

    UnitTestRunnerUtil.unload_modules(module_name)

    return result
