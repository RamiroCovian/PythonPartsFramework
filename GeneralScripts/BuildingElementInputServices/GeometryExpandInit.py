""" implementation of the geometry expand initialization
"""

# pylint: disable=global-statement

from __future__ import annotations

from typing import TYPE_CHECKING

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Reinforcement as AllplanReinf
import NemAll_Python_Utility as AllplanUtil

from InputMode import InputMode

if TYPE_CHECKING:
    from .InputData import InputData

ASK_3D_KEY = "DO_NOT_ASK_3D_REINFORCEMENT"
USE_3D_KEY = "USE_3D_REINFORCEMENT"

if ASK_3D_KEY not in globals():
    globals()[ASK_3D_KEY] = False
    globals()[USE_3D_KEY] = False

DO_NOT_ASK_3D_REINFORCEMENT = globals()[ASK_3D_KEY]
USE_3D_REINFORCEMENT        = globals()[USE_3D_KEY]

class GeometryExpandInit():
    """ implementation of the geometry expand initialization
    """

    @staticmethod
    def execute(input_data: InputData,
                msg_info  : AllplanIFW.AddMsgInfo):
        """ initialize the geometry expand

        Args:
            input_data: input data
            msg_info:   additional mouse message info
        """

        if input_data.last_input_doc is not None:
            AllplanBaseEle.GetViewMatrices(input_data.last_input_doc)

        is_3d_reinf = AllplanReinf.ReinforcementSettings.Is3DReinforcement()

        global DO_NOT_ASK_3D_REINFORCEMENT
        global USE_3D_REINFORCEMENT

        if not DO_NOT_ASK_3D_REINFORCEMENT and not is_3d_reinf:
            msg = input_data.str_table_service.get_string("e_USE_3D_REINFORCEMENT",
                                                          "'Reinforce with 3D-Model' ist disabled: Enable for the PythonPart?")

            result = AllplanUtil.ShowMessageBox(msg, AllplanUtil.MB_YESNO | AllplanUtil.MB_DONOTASKAGAIN)

            DO_NOT_ASK_3D_REINFORCEMENT = result & AllplanUtil.MB_DONOTASKAGAIN

            result -= DO_NOT_ASK_3D_REINFORCEMENT

            USE_3D_REINFORCEMENT = result == AllplanUtil.IDYES

        input_data.expand_util = AllplanReinf.GeometryExpansionUtil(msg_info, is_3d_reinf | USE_3D_REINFORCEMENT)
        input_data.input_mode  = InputMode.GeoExpand
