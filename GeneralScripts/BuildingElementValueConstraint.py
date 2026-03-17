""" Implementation of the building element value constraint
"""

from typing import Any

import re

import NemAll_Python_Reinforcement as AllplanReinf

from BuildingElement import BuildingElement
from BuildingElementControlProperties import BuildingElementControlProperties
from ControlProperties import ControlProperties
from ParameterProperty import ParameterProperty

from ValueTypes.ParameterPropertyValueTypes import ParameterPropertyValueTypes
from ValueTypes.ParameterPropertyValueTypesImpl import ParameterPropertyValueTypesImpl

class BuildingElementValueConstraint():
    """ Implementation of the functions for the building element value constraint
    """

    name_mapping = "__"

    @staticmethod
    def _update_data(data_dict : dict[str, Any],
                     build_ele : BuildingElement,
                     ctrl_props: ControlProperties):
        """ Update the data

        Args:
            data_dict:  dict with the parameter data
            build_ele:  building element with the parameter properties
            ctrl_props: control properties
        """

        for constraint_name in ctrl_props.constraint:
            if BuildingElementValueConstraint.name_mapping not in constraint_name:
                if (prop := build_ele.get_property(constraint_name)):
                    if (value_type := prop.value_type) == ParameterPropertyValueTypes.ANGLE_COMBO_BOX:
                        value_type = ParameterPropertyValueTypesImpl.get_value_type_impl(ParameterPropertyValueTypes.ANGLE)

                    data_dict[value_type] = prop.value

            else:
                key_value = constraint_name.replace("_", "").replace(" ", "").split("=")

                prop = build_ele.get_property(key_value[1])

                data_dict[key_value[0].lower()] = prop.value if prop else eval(key_value[1])


    @staticmethod
    def _update_reinfbarhooklength(build_ele       : BuildingElement,
                                   hook_length_prop: ParameterProperty,
                                   ctrl_props      : ControlProperties):
        """ Update the bar hook length

        Args:
            build_ele:        building element with the parameter properties
            hook_length_prop: hook length property
            ctrl_props:       control properties
        """

        data_dict = {"reinfbardiameter"   : 0,
                     "reinfsteelgrade"    : AllplanReinf.ReinforcementSettings.GetSteelGrade(),
                     "reinfconcretegrade" : AllplanReinf.ReinforcementSettings.GetConcreteGrade(),
                     "angle"              : 90,
                     "reinfhooktype"      : AllplanReinf.HookType.eAnchorage}

        BuildingElementValueConstraint._update_data(data_dict, build_ele, ctrl_props)

        length_service = AllplanReinf.HookLengthService(AllplanReinf.ReinforcementSettings.GetNorm(),
                                                        data_dict["reinfconcretegrade"], data_dict["reinfsteelgrade"], True)

        hook_length_prop.value = length_service.GetHookLength(data_dict["angle"],
                                                              AllplanReinf.HookType(data_dict["reinfhooktype"]),
                                                              data_dict["reinfbardiameter"])

    @staticmethod
    def _update_reinfmeshhooklength(build_ele       : BuildingElement,
                                    hook_length_prop: ParameterProperty,
                                    ctrl_props      : ControlProperties):
        """ Update the mesh hook length

        Args:
            build_ele:        building element with the parameter properties
            hook_length_prop: hook length property
            ctrl_props:       control properties
        """

        data_dict = {"reinfmeshtype"             : "",
                     "reinfsteelgrade"           : AllplanReinf.ReinforcementSettings.GetSteelGrade(),
                     "reinfconcretegrade"        : AllplanReinf.ReinforcementSettings.GetConcreteGrade(),
                     "angle"                     : 90,
                     "reinfhooktype"             : AllplanReinf.HookType.eAnchorage,
                     "reinfmeshbendingdirection" : AllplanReinf.MeshBendingDirection.LongitudinalBars}

        BuildingElementValueConstraint._update_data(data_dict, build_ele, ctrl_props)

        mesh_data = AllplanReinf.ReinforcementShapeBuilder.GetMeshData(data_dict["reinfmeshtype"])

        diameter = mesh_data.DiameterLongitudinal \
                   if data_dict["reinfmeshbendingdirection"] == AllplanReinf.MeshBendingDirection.LongitudinalBars else \
                   mesh_data.DiameterCross

        length_service = AllplanReinf.HookLengthService(AllplanReinf.ReinforcementSettings.GetNorm(),
                                                        data_dict["reinfconcretegrade"], data_dict["reinfsteelgrade"], True)

        hook_length_prop.value = length_service.GetHookLength(data_dict["angle"],
                                                              AllplanReinf.HookType(data_dict["reinfhooktype"]), diameter)


    @staticmethod
    def _update_reinfhooklength(build_ele       : BuildingElement,
                                hook_length_prop: ParameterProperty,
                                ctrl_props      : ControlProperties):
        """ Update the hook length

        Args:
            build_ele:        building element with the parameter properties
            hook_length_prop: hook length property
            ctrl_props:       control properties
        """

        for constraint_name in ctrl_props.constraint:
            if BuildingElementValueConstraint.name_mapping not in constraint_name:
                if (prop := build_ele.get_property(constraint_name)):
                    if prop.value_type == ParameterPropertyValueTypes.REINF_BAR_DIAMETER:
                        BuildingElementValueConstraint._update_reinfbarhooklength(build_ele, hook_length_prop, ctrl_props)

                    elif prop.value_type == ParameterPropertyValueTypes.REINF_MESH_TYPE:
                        BuildingElementValueConstraint._update_reinfmeshhooklength(build_ele, hook_length_prop, ctrl_props)

    @staticmethod
    def check_property_constraint(modified_name          : str,
                                  build_ele     : BuildingElement,
                                  ctrl_prop_list: BuildingElementControlProperties) -> bool:
        """ Check for a property constraint

        Args:
            name:           name of the modified property
            build_ele:      building element with the parameter properties
            ctrl_prop_list: control properties

        Returns:
            update state
        """

        is_update = False

        updated_names : set[str] = set()

        modified_names = [modified_name.split("[", 1)[0].split(".", 1)[0]]


        #----------------- loop over the modified names

        while modified_names:
            if (modified_name := modified_names[0]) in updated_names:
                del modified_names[0]
                continue


            #------------- check the constraints which include the modified named

            for ctrl_prop in ctrl_prop_list:
                if not ctrl_prop.constraint or ctrl_prop.value_name == modified_name:
                    continue

                if not (prop := build_ele.get_property(ctrl_prop.value_name)):
                    continue

                for constraint in ctrl_prop.constraint:
                    constraint_value = re.split("(?<!=)==(?!=)", constraint)[-1].replace("_", "")

                    if not re.search(r"\b" + modified_name + r"\b", constraint_value):
                        continue


                    #--------- get the property for the constraint

                    if (update_fct := getattr(prop.value_type, "update_by_constraint", None)) is not None:
                        update_fct(build_ele, prop, ctrl_prop, modified_name)

                        is_update = True

                        if ctrl_prop.value_name not in modified_names:
                            modified_names.append(ctrl_prop.value_name)

                        break

                    if (update_fct := getattr(BuildingElementValueConstraint, "_update_" + prop.value_type, None)) is not None:
                        update_fct(build_ele, prop, ctrl_prop)

                        is_update = True

                        if ctrl_prop.value_name not in modified_names:
                            modified_names.append(ctrl_prop.value_name)

                        break

            updated_names.add(modified_name)

            del modified_names[0]

        return is_update


    @staticmethod
    def check_property_constraint_init(build_ele     : BuildingElement,
                                       ctrl_prop_list: BuildingElementControlProperties):
        """ Check for a property constraint initialization

        Args:
            build_ele:      building element with the parameter properties
            ctrl_prop_list: control properties
        """

        for ctrl_prop in ctrl_prop_list:
            if not ctrl_prop.constraint:
                continue

            prop = build_ele.get_property(ctrl_prop.value_name)

            if prop and (prop.value == -1 or prop.value_type.is_default_init_by_constraint(build_ele, ctrl_prop)):
                if (update_fct := getattr(prop.value_type, "update_by_constraint", None)) is not None:
                    update_fct(build_ele, prop, ctrl_prop, "")
                else:
                    BuildingElementValueConstraint.check_property_constraint(ctrl_prop.constraint[0], build_ele, ctrl_prop_list)


    @staticmethod
    def update_enable_by_constraint(build_ele     : BuildingElement,
                                    ctrl_prop_list: BuildingElementControlProperties):
        """ Check for a property constraint initialization

        Args:
            build_ele:      building element with the parameter properties
            ctrl_prop_list: control properties
        """

        for ctrl_prop in ctrl_prop_list:
            if not ctrl_prop.constraint:
                continue

            if (prop := build_ele.get_property(ctrl_prop.value_name)) is not None:
                prop.value_type.update_enable_by_constraint(build_ele, prop, ctrl_prop)
