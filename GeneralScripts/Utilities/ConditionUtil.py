""" implementation of the condition utilities
"""

from typing import Any

from .GeneralConstants import GeneralConstants

class ConditionUtil():
    """ implementation of the condition utilities
    """

    @staticmethod
    def modify_condition(value_name: str,
                         condition : str,
                         value     : str) -> str:
        """ Modify the condition

        Args:
            value_name: name of the value
            condition:  visible condition
            value:      condition value

        Returns:
            modified condition
        """

        if GeneralConstants.SUB_NAME_SEPARATOR not in value_name:
            if GeneralConstants.TEXT_SEPARATOR not in condition:
                return value

            return value + GeneralConstants.TEXT_SEPARATOR + condition.split(GeneralConstants.TEXT_SEPARATOR, 1)[-1]

        sub_conds = condition.split(GeneralConstants.TEXT_SEPARATOR)

        value_name += ":"

        for index, sub_cond in enumerate(sub_conds):
            if sub_cond.startswith(value_name):
                sub_conds[index] = value_name + value

                return GeneralConstants.TEXT_SEPARATOR.join(sub_conds)

        return condition + GeneralConstants.TEXT_SEPARATOR + value_name + value


    @staticmethod
    def get_condition_dict(condition_str: str,
                           value_name   : str,
                           param_dict   : dict[str, Any]) -> dict[str, bool]:
        """ Get the condition dictionary

        Args:
            condition_str: condition
            value_name:    value name
            param_dict:    parameter dictionary

        Returns:
            condition dictionary
        """

        if not condition_str:
            return {}

        condition_list = condition_str.split(GeneralConstants.TEXT_SEPARATOR)

        condition_dict = {}

        for condition in condition_list:
            if (ip_colon := condition.find(":")) == -1:
                continue

            name = condition[:ip_colon]

            if (ip_bracket := value_name.find("[")) != -1:
                index = value_name[ip_bracket: value_name.rfind("]") + 1]

                if GeneralConstants.SUB_NAME_SEPARATOR in name:
                    name = name.replace("." , index + GeneralConstants.SUB_NAME_SEPARATOR)
                else:
                    name += index

            condition_dict[name] = eval(condition[ip_colon + 1:], param_dict)

        return condition_dict
