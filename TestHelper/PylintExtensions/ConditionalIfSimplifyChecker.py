""" implementation of the conditional if simplify checker
"""

from typing import TYPE_CHECKING

from astroid import nodes

from .BaseCustomChecker import BaseCustomChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

CONDITION_SIMPLIFY_OR   = "condition simplify or"
CONDITION_SIMPLIFY_SWAP = "condition simplify swap"
CONDITION_SIMPLIFY_IN   = "condition simplify in"

class ConditionalIfSimplifyChecker(BaseCustomChecker):
    """ implementation of the conditional if simplify checker
    """

    msgs = {"R5001": ("Replace if-expressiong with 'or': %s.",
                      CONDITION_SIMPLIFY_OR, ""),
            "R5002": ("Swap if/else branch to avoid 'if not'",
                      CONDITION_SIMPLIFY_SWAP, ""),
            "R5003": ("Use 'in' for substring test:",
                      CONDITION_SIMPLIFY_IN, "")
           }

    def visit_assign(self,
                     node: nodes.Assign):
        """ visit the value assign

        Args:
            node: node of the Assign
        """

        line = self._get_current_line(node)

        if " if " not in line:
            if ".find(" in line and "-1" in line and ("!=" in line or "==" in line):
                self.add_message(CONDITION_SIMPLIFY_IN,
                                node = node)

            return

        if " if not " in line:
            self.add_message(CONDITION_SIMPLIFY_SWAP, node = node)

            return

        line = line.split("=")[-1]

        left_value, _, right = line.partition(" if ")

        cond_value, _, right_value = right.partition(" else ")

        if left_value.strip() == cond_value.strip():
            self.add_message(CONDITION_SIMPLIFY_OR,
                             node = node,
                             args =(f"{left_value} or {right_value}",))


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """

    linter.register_checker(ConditionalIfSimplifyChecker(linter))
