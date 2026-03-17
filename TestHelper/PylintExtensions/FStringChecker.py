""" implementation of the f string checker
"""

from typing import TYPE_CHECKING

from astroid import nodes

from .BaseCustomChecker import BaseCustomChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

F_STRING_USE = "use f-string"

class FStringChecker(BaseCustomChecker):
    """ implementation of the f string checker
    """

    msgs = {"R5021": ("Use f-string for string concatenation:",
                      F_STRING_USE, "")
           }

    def visit_binop(self,
                    node: nodes.BinOp):
        """ visit the if statement

        Args:
            node: node of the if
        """

        if node.op != "+":
            return

        line = self._get_current_line(node)

        if "\"" not in line or "f\"" in line or "fr\"" in line:
            return

        while (open_bracket := line.find("(")) != -1 and open_bracket < line.find("\""):
            line = line[open_bracket + 1:]

        for part in self.split_by_comma(line):
            if ("+ \"" in part or "\" +" in part):
                self.add_message(F_STRING_USE, node = node)


def register(linter: "PyLinter") -> None:
    """This required method auto registers the checker during initialization.
    :param linter: The linter to register the checker to.
    """
    linter.register_checker(FStringChecker(linter))
