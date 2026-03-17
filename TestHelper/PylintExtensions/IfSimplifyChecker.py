""" implementation of the if simplify checker
"""

from typing import TYPE_CHECKING

from astroid import nodes

from .BaseCustomChecker import BaseCustomChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

IF_SIMPLIFY = "substring test simplify"

class IfSimplifyChecker(BaseCustomChecker):
    """ implementation of the if simplify checker
    """

    msgs = {"R5011": ("Use 'in' for substring test:",
                      IF_SIMPLIFY, "")
           }

    def visit_if(self,
                 node: nodes.If):
        """ visit the if statement

        Args:
            node: node of the if
        """

        line = self._get_current_line(node)

        if ".find(" not in line or "-1" not in line or ":=" in line:
            return

        self.add_message(IF_SIMPLIFY,
                         node = node)


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(IfSimplifyChecker(linter))
