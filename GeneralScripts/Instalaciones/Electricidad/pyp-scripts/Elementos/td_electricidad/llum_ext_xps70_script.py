# -*- coding: utf-8 -*-
# pylint: disable=import-error,broad-exception-caught
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .llum_ext_xps70_3D import LlumExtXPS703D


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    obj = LlumExtXPS703D()
    model_ele_list = obj.create_geometry_3d()
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return LlumExtXPS70Script(build_ele, script_object_data)


class LlumExtXPS70Script(BaseScriptObject):
    """Llum Exterior XPS 70 - TD Electricitat."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele

    def execute(self) -> CreateElementResult:
        obj = LlumExtXPS703D()
        model_ele_list = obj.create_geometry_3d(color=1)
        return CreateElementResult(model_ele_list)
