""" Definition of the input data
"""

# pylint: disable=too-many-instance-attributes

from typing import Any, cast, TYPE_CHECKING

import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_IFW_ElementAdapter as AllplanEleAdapter
import NemAll_Python_IFW_Input as AllplanIFW
import NemAll_Python_Reinforcement as AllplanReinf

from BaseInteractor import BaseInteractor
from BaseScriptObject import BaseScriptObject
from BuildingElement import BuildingElement
from BuildingElementComposite import BuildingElementComposite
from BuildingElementListService import BuildingElementListService
from BuildingElementService import BuildingElementService
from BuildingElementSubElementUtil import BuildingElementSubElementUtil
from BuildingElementControlProperties import BuildingElementControlProperties
from BuildingElementValueConstraint import BuildingElementValueConstraint
from BuildingElementXML import BuildingElementXML
from CreateElementResult import CreateElementResult
from DocumentManager import DocumentManager
from HandleModificationService import HandleModificationService
from InputMode import InputMode
from StringTableService import StringTableService

from TypeCollections.ModificationElementList import ModificationElementList

from TestHelper.Mock.CoordinateInputMock import CoordinateInputMock

from .AttributeTakeoverService import AttributeTakeoverService
from .GeometryExpandInit import GeometryExpandInit

if TYPE_CHECKING:
    from BuildingElementPaletteService import BuildingElementPaletteService

class InputData:
    """ Definition of the input data
    """

    def __init__(self,
                 coord_input: AllplanIFW.CoordinateInput,
                 path       : str)                      :
        """ Initialization of class BuildingElementInputData

        Args:
            coord_input:    Coordinate input class
            path:           Python script path
        """

        if isinstance(coord_input, AllplanEleAdapter.DocumentAdapter):
            coord_input = cast(AllplanIFW.CoordinateInput, CoordinateInputMock(coord_input))

        self.coord_input = coord_input

        self.build_ele_list           : list[BuildingElement]                         = []
        self.build_ele_script         : Any                                           = Any
        self.build_ele_ctrl_props_list: list[BuildingElementControlProperties]        = []
        self.interactor               : (BaseInteractor | None)                       = None
        self.script_object            : (BaseScriptObject | None)                     = None
        self.expand_util              : (AllplanReinf.GeometryExpansionUtil | None)   = None
        self.palette_service          : (BuildingElementPaletteService | None)        = None
        self.last_input_doc           : AllplanEleAdapter.DocumentAdapter
        self.last_view_proj           : AllplanIFW.ViewWorldProjection
        self.build_ele_composite      : (BuildingElementComposite | None)             = None
        self.asso_ref_ele             : (AllplanEleAdapter.BaseElementAdapter | None) = None

        self.input_mode            = InputMode.RefPoint
        self.build_ele_service     = BuildingElementService()
        self.file_name             = ""
        self.insert_matrix         = AllplanGeo.Matrix3D()
        self.modification_ele_list = ModificationElementList()
        self.active_page           = 0
        self.create_ele_result     = CreateElementResult()
        self.old_build_ele_list    = []
        self.last_expanded         = False
        self.b_insert_point        = False
        self.is_only_update        = False
        self.is_modify_elements    = False
        self.is_modified_parameter = False
        self.handle_modi_service   = HandleModificationService(coord_input, self.build_ele_list, self.build_ele_ctrl_props_list,
                                                               None, not self.modification_ele_list.is_modification_element())

        self.str_table_service = StringTableService(path)


    def init_general_data(self,
                          is_modification_mode: bool,
                          modify_uuid_list    : ModificationElementList,
                          asso_ref_ele        : AllplanEleAdapter.BaseElementAdapter,
                          is_only_update      : bool):
        """ initialize the general data

        Args:
            is_modification_mode: is started in modification mode
            modify_uuid_list:     list with the UUIDs of the modified elements
            asso_ref_ele:         reference element of the associative view
            is_only_update:       only update the PythonPart, no user interaction
        """

        modification_ele_list = ModificationElementList(modify_uuid_list)

        DocumentManager.get_instance().set_pythonpart_element(modification_ele_list)
        DocumentManager.get_instance().asso_ref_element = asso_ref_ele

        self.last_input_doc = self.coord_input.GetInputViewDocument()
        self.last_view_proj = self.coord_input.GetViewWorldProjection()
        self.asso_ref_ele   = asso_ref_ele
        self.is_only_update = is_only_update

        if is_modification_mode:
            self.modification_ele_list.extend(modification_ele_list)
        else:
            self.modification_ele_list.append(ModificationElementList.EMPTY_GUID)


    def prepare_script_data(self,
                            parameter_data        : list[str],
                            msg_info              : (AllplanIFW.AddMsgInfo | None),
                            is_modification_mode  : bool,
                            geo_matrix            : AllplanGeo.Matrix3D,
                            local_placement_matrix: AllplanGeo.Matrix3D):
        """ prepare the script data

        Args:
            parameter_data:         parameter data of the selected PythonPart
            msg_info:               additional mouse message info
            is_modification_mode:   is started in modification mode
            geo_matrix:             placement matrix
            local_placement_matrix: local placement matrix
        """

        #----------------- get the values from the parameters

        if parameter_data:
            BuildingElementListService.read_fav_data(parameter_data, self.build_ele_list,
                                                     is_modification_mode = is_modification_mode,
                                                     script = self.build_ele_script)

            for build_ele, ctrl_prop_list in zip(self.build_ele_list, self.build_ele_ctrl_props_list):
                BuildingElementValueConstraint.update_enable_by_constraint(build_ele, ctrl_prop_list)
                BuildingElementValueConstraint.check_property_constraint_init(build_ele, ctrl_prop_list)

            AttributeTakeoverService.check_external_attribute_modification(self.build_ele_list)


        #----------------- set the data for the modification mode

        if is_modification_mode:
            update_matrix = self.calculate_update_matrix(geo_matrix, local_placement_matrix)

            self.build_ele_list[0].set_insert_matrix(AllplanGeo.Matrix3D(update_matrix))

            self.b_insert_point = True
            self.insert_matrix  = self.build_ele_list[0].get_insert_matrix()
            self.input_mode     = InputMode.HandleSelect


        #------------------ Initialize the geometry expansion utility

        elif self.build_ele_list[0].geometry_expand and msg_info is not None:
            GeometryExpandInit.execute(self, msg_info)


    def set_insert_matrix_from_point(self,
                                     pnt: AllplanGeo.Point3D):
        """ Set the translation into the insert matrix

        Args:
            pnt: input point
        """

        angle = AllplanGeo.Angle()

        if not self.is_modify_elements and self.script_object is None:
            angle.Rad = self.coord_input.GetInputControlValue()

        self.insert_matrix.SetRotation(AllplanGeo.Line3D(AllplanGeo.Point3D(), AllplanGeo.Point3D(0, 0, 1000)), angle)

        trans_vec = AllplanGeo.Vector3D(pnt)

        self.insert_matrix.SetTranslation(trans_vec)

        self.build_ele_list[0].set_insert_matrix(AllplanGeo.Matrix3D(self.insert_matrix))


    @staticmethod
    def calculate_update_matrix(geo_matrix            : AllplanGeo.Matrix3D,
                                local_placement_matrix: AllplanGeo.Matrix3D) -> AllplanGeo.Matrix3D:
        """ Calculate matrix for update

        Args:
            geo_matrix:             geometry matrix
            local_placement_matrix: local placement matrix

        Returns:
            original insert matrix of the PythonPart
        """

        local_pl__tmp_inv = AllplanGeo.Matrix3D(local_placement_matrix)
        local_pl__tmp_inv.GaussInvert()

        return local_pl__tmp_inv * geo_matrix
