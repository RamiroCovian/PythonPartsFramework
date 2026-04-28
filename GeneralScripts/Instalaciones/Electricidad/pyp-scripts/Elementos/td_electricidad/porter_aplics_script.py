# -*- coding: utf-8 -*-
# pylint: disable=import-error,broad-exception-caught
from BaseScriptObject import BaseScriptObject, BaseScriptObjectData
from BuildingElement import BuildingElement
from CreateElementResult import CreateElementResult

from .porter_aplics_3D import PorterAplics3D


def check_allplan_version(build_ele, version):
    return True


def create_preview(build_ele, script_object_data):
    obj = PorterAplics3D()
    model_ele_list = obj.create_geometry_3d()
    return model_ele_list, []


def create_script_object(build_ele, script_object_data):
    return PorterAplicsScript(build_ele, script_object_data)


class PorterAplicsScript(BaseScriptObject):
    """Porter i Aplics - TD Electricitat."""

    def __init__(
        self, build_ele: BuildingElement, script_object_data: BaseScriptObjectData
    ):
        super().__init__(script_object_data)
        self.build_ele = build_ele

    def execute(self) -> CreateElementResult:
        obj = PorterAplics3D()
        model_ele_list = obj.create_geometry_3d(color=1)
        return CreateElementResult(model_ele_list)
