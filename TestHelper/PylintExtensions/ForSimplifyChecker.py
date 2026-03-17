""" implementation of the if simplify checker
"""

from typing import TYPE_CHECKING

from astroid import nodes

from .BaseCustomChecker import BaseCustomChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

FOR_SIMPLIFY = "use iter"

class ForSimplifyChecker(BaseCustomChecker):
    """ implementation of the if simplify checker
    """

    msgs = {"R5031": ("Replace for-loop with 'iter(%s)'.",
                      FOR_SIMPLIFY, "")
           }

    def visit_comprehension(self,
                            node: nodes.Comprehension):
        """ visit the for statement

        Args:
            node: node of the for
        """

        line = self._get_current_line(node).strip()

        if line.startswith("for ") or not line.endswith(")"):
            return

        line = line.split("(", 1)[-1][:-1]

        value, _, right    = line.partition(" for ")
        index, _, elements = right.partition(" in ")

        if len(elements.split(" ")) > 1 or value.strip() != index.strip():
            return

        self.add_message(FOR_SIMPLIFY,
                         node = node,
                         args = (elements, ))


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(ForSimplifyChecker(linter))
