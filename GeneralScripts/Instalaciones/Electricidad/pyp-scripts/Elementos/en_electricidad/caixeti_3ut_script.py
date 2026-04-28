# -*- coding: utf-8 -*-
# pylint: disable=import-error,broad-exception-caught
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .caixeti_3ut_3D import Caixeti3UTObject3D


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    obj = Caixeti3UTObject3D()
    model_ele_list = obj.create_geometry_3d()
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return Caixeti3UTScript(build_ele, script_object_data)


class Caixeti3UTScript(BaseScriptObject):
    """Caixeti 3 UT - EN Electricitat."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele

    def execute(self) -> CreateElementResult:
        obj = Caixeti3UTObject3D()
        model_ele_list = obj.create_geometry_3d()
        return CreateElementResult(model_ele_list)
