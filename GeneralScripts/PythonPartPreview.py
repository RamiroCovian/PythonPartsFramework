""" Implementation of the PythonPart preview
"""

from typing import Any

import NemAll_Python_BaseElements as AllplanBaseEle
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_Geometry as AllplanGeo

from Utilities.SystemAngleUtil import SystemAngleUtil

class PythonPartPreview():
    """ Implementation of the PythonPart transaction """

    __preview_draw_lock = False

    @staticmethod
    def execute(doc              : AllplanEleAdapter.DocumentAdapter,
                placement_matrix : AllplanGeo.Matrix3D,
                model_ele_list   : list[Any],
                direct_draw      : bool                                          = False,
                asso_ref_object  : (AllplanEleAdapter.BaseElementAdapter | None) = None,
                use_system_angle : bool                                          = True,
                as_static_preview: bool                                          = False):
        """ execute the preview draw

        Args:
            doc:               document of the Allplan drawing files
            placement_matrix:  placement matrix
            model_ele_list:    list with the model elements
            direct_draw:       direct draw of the preview
            asso_ref_object:   associative view reference object
            use_system_angle:  use the system angle state
            as_static_preview: draw as static preview state
        """

        if not model_ele_list or PythonPartPreview.__preview_draw_lock:
            return


        #----------------- final transformation in case of rotated crosshair

        if use_system_angle:
            placement_matrix = SystemAngleUtil.execute_rotation(placement_matrix)


        #----------------- draw the preview

        AllplanBaseEle.DrawElementPreview(doc, placement_matrix, model_ele_list, direct_draw, asso_ref_object, as_static_preview)


    @staticmethod
    def close():
        """ close the preview
        """

        if PythonPartPreview.__preview_draw_lock:
            return

        AllplanBaseEle.CloseElementPreview()
        AllplanBaseEle.ClearElementPreview()


    @staticmethod
    def set_preview_draw_lock(preview_draw_lock: bool):
        """ set the preview draw lock state

        Args:
            preview_draw_lock: preview draw lock state
        """

        PythonPartPreview.__preview_draw_lock = preview_draw_lock
